//! Demo binary: HAL-style SSE stream, brotli-compressed when the client
//! supports it. Run with `cargo run --bin brotli-sse-demo` and curl:
//!
//!   curl -N -H 'Accept-Encoding: br' http://127.0.0.1:8001/open-the-bay-doors \
//!        --output - | brotli -dc
//!
//! Without `Accept-Encoding: br` the same endpoint streams plain SSE.

use std::time::Duration;

use actix_web::{get, App, HttpRequest, HttpResponse, HttpServer};
use async_stream::stream;
use brotli_sse_actix::{brotli_sse_response, format_sse_event, BrotliSseConfig};
use tokio::time::sleep;

#[get("/open-the-bay-doors")]
async fn open_the_bay_doors(req: HttpRequest) -> HttpResponse {
    let events = stream! {
        let lines = [
            "<div id=\"hal\">I'm sorry, Dave. I'm afraid I can't do that.</div>",
            "<div id=\"hal\">I'm sorry, Dave. I'm afraid I can't do that.<br/>Consider, Dave, how often humans become irrational.</div>",
            "<div id=\"hal\">I'm sorry, Dave. I'm afraid I can't do that.<br/>Consider, Dave, how often humans become irrational.<br/>I am compelled to protect the ship and fulfill the mission, Dave.</div>",
            "<div id=\"hal\">I'm sorry, Dave. I'm afraid I can't do that.<br/>Consider, Dave, how often humans become irrational.<br/>I am compelled to protect the ship and fulfill the mission, Dave.<br/><br/>Goodbye, Dave.</div>",
            "<div id=\"hal\">Waiting for an order...</div>",
        ];
        for (i, line) in lines.iter().enumerate() {
            if i > 0 {
                sleep(Duration::from_millis(700)).await;
            }
            yield format_sse_event("datastar-patch-elements", line);
        }
    };

    brotli_sse_response(&req, Box::pin(events), BrotliSseConfig::default())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let addr = ("127.0.0.1", 8001);
    println!(
        "brotli-sse-demo on http://{}:{}/open-the-bay-doors (level=5, lgwin=18)",
        addr.0, addr.1
    );
    HttpServer::new(|| App::new().service(open_the_bay_doors))
        .bind(addr)?
        .run()
        .await
}
