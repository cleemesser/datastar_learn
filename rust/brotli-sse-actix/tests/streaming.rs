//! Integration tests for the brotli SSE handler.
//!
//! Two things we have to prove:
//!   1. The brotli stream actually decodes back to the original SSE bytes.
//!   2. Chunks arrive *incrementally* — i.e. the per-event flush works and
//!      we are not falling back to actix's batching behaviour. This is the
//!      whole point of doing brotli inside the handler.

use std::io::Read;
use std::net::TcpListener;
use std::time::{Duration, Instant};

use actix_web::{get, web, App, HttpRequest, HttpResponse, HttpServer};
use async_stream::stream;
use brotli::Decompressor;
use brotli_sse_actix::{brotli_sse_response, format_sse_event, BrotliSseConfig};
use tokio::sync::oneshot;
use tokio::time::sleep;

const EVENT_GAP: Duration = Duration::from_millis(250);
const EVENTS: &[&str] = &[
    "<div id=\"hal\">one</div>",
    "<div id=\"hal\">one\ntwo</div>",
    "<div id=\"hal\">one\ntwo\nthree</div>",
];

#[get("/sse")]
async fn sse(req: HttpRequest, state: web::Data<TestConfig>) -> HttpResponse {
    let cfg = state.cfg;
    let events = stream! {
        for (i, line) in EVENTS.iter().enumerate() {
            if i > 0 {
                sleep(EVENT_GAP).await;
            }
            yield format_sse_event("datastar-patch-elements", line);
        }
    };
    brotli_sse_response(&req, Box::pin(events), cfg)
}

#[derive(Clone, Copy)]
struct TestConfig {
    cfg: BrotliSseConfig,
}

struct TestServer {
    addr: String,
    shutdown: Option<oneshot::Sender<()>>,
    join: Option<std::thread::JoinHandle<()>>,
}

impl TestServer {
    fn start(cfg: BrotliSseConfig) -> Self {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
        let addr = format!("http://{}", listener.local_addr().unwrap());
        let (tx, rx) = oneshot::channel::<()>();

        let join = std::thread::spawn(move || {
            let rt = tokio::runtime::Builder::new_current_thread()
                .enable_all()
                .build()
                .unwrap();
            rt.block_on(async move {
                let state = TestConfig { cfg };
                let server = HttpServer::new(move || {
                    App::new()
                        .app_data(web::Data::new(state))
                        .service(sse)
                })
                .listen(listener)
                .unwrap()
                .workers(1)
                .run();
                let handle = server.handle();
                tokio::spawn(async move {
                    let _ = rx.await;
                    handle.stop(true).await;
                });
                let _ = server.await;
            });
        });

        // Tiny wait so the server is listening before tests fire requests.
        std::thread::sleep(Duration::from_millis(50));

        Self { addr, shutdown: Some(tx), join: Some(join) }
    }
}

impl Drop for TestServer {
    fn drop(&mut self) {
        if let Some(tx) = self.shutdown.take() {
            let _ = tx.send(());
        }
        if let Some(join) = self.join.take() {
            let _ = join.join();
        }
    }
}

fn expected_sse_bytes() -> Vec<u8> {
    let mut s = String::new();
    for line in EVENTS {
        s.push_str(&format_sse_event("datastar-patch-elements", line));
    }
    s.into_bytes()
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn brotli_round_trip_decodes_to_original_sse() {
    let server = TestServer::start(BrotliSseConfig::default());
    let url = format!("{}/sse", server.addr);

    let client = reqwest::Client::builder().build().unwrap();
    // Disable reqwest's automatic brotli decoding — we want the raw bytes
    // so we can verify the body is actually compressed.
    let resp = client
        .get(&url)
        .header("Accept-Encoding", "br")
        .send()
        .await
        .expect("send");

    assert_eq!(resp.status(), 200);
    assert_eq!(
        resp.headers()
            .get("content-encoding")
            .and_then(|v| v.to_str().ok()),
        Some("br")
    );
    assert_eq!(
        resp.headers()
            .get("content-type")
            .and_then(|v| v.to_str().ok()),
        Some("text/event-stream")
    );

    let body = resp.bytes().await.expect("body").to_vec();
    let mut decoder = Decompressor::new(body.as_slice(), 4096);
    let mut decoded = Vec::new();
    decoder.read_to_end(&mut decoded).expect("decompress");

    assert_eq!(decoded, expected_sse_bytes());
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn identity_fallback_when_no_br_in_accept_encoding() {
    let server = TestServer::start(BrotliSseConfig::default());
    let url = format!("{}/sse", server.addr);

    let client = reqwest::Client::builder().build().unwrap();
    let resp = client
        .get(&url)
        .header("Accept-Encoding", "gzip, deflate")
        .send()
        .await
        .expect("send");

    assert_eq!(resp.status(), 200);
    assert!(resp.headers().get("content-encoding").is_none());
    let body = resp.bytes().await.expect("body").to_vec();
    assert_eq!(body, expected_sse_bytes());
}

/// The whole point of doing brotli in the handler: chunks must arrive
/// *progressively*, not all at the end. We assert at least one body chunk
/// shows up before the second event has even been produced.
#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn br_chunks_arrive_incrementally() {
    use futures::stream::StreamExt;

    let server = TestServer::start(BrotliSseConfig::default());
    let url = format!("{}/sse", server.addr);

    let client = reqwest::Client::builder().build().unwrap();
    let resp = client
        .get(&url)
        .header("Accept-Encoding", "br")
        .send()
        .await
        .expect("send");

    assert_eq!(
        resp.headers()
            .get("content-encoding")
            .and_then(|v| v.to_str().ok()),
        Some("br")
    );

    let started = Instant::now();
    let mut stream = resp.bytes_stream();

    // First chunk is the first event's compressed payload. It must arrive
    // well before EVENT_GAP × (EVENTS.len() - 1) — i.e. before all events
    // are even produced. If actix's middleware were buffering, we'd block
    // until the body is finalized.
    let first = stream.next().await.expect("first chunk").expect("ok");
    let first_arrived = started.elapsed();
    assert!(
        !first.is_empty(),
        "first chunk should carry the first event, got empty"
    );
    let max_first = EVENT_GAP / 2;
    assert!(
        first_arrived < max_first,
        "first chunk took {:?}, expected < {:?} (compression is batching)",
        first_arrived,
        max_first
    );

    // Drain the rest so the connection closes cleanly.
    let mut total = first.len();
    while let Some(next) = stream.next().await {
        total += next.expect("ok").len();
    }
    assert!(total > 0);
}
