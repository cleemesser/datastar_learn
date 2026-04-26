//! Streaming brotli compression for SSE on actix-web.
//!
//! Why this exists: actix-web's `middleware::Compress` buffers streaming
//! response bodies (see actix/actix-web#3410), so SSE events get batched and
//! arrive at the client all at once. It also doesn't expose `lgwin`, which is
//! the brotli knob that actually matters for long-lived SSE streams — Murphy's
//! benchmarks show lgwin=18 (~263 KB sliding window) takes ratios from ~30:1
//! to 150-250:1 on typical Datastar payloads, while quality stays at 5.
//!
//! Design: brotli runs *inside* the handler. We hold one `CompressorWriter`
//! per connection, write each SSE event into it, then call `flush()` (which
//! emits a brotli FLUSH block — no dictionary reset, just pushes pending
//! bytes to the wire). The encoded chunk goes out as a single body chunk,
//! keeping per-event delivery semantics intact.

use std::io::Write;
use std::sync::{Arc, Mutex};

use actix_web::http::header::{self, HeaderValue};
use actix_web::{HttpRequest, HttpResponse};
use brotli::CompressorWriter;
use bytes::Bytes;
use futures::stream::{Stream, StreamExt};

/// Tuning for the per-connection brotli encoder.
#[derive(Debug, Clone, Copy)]
pub struct BrotliSseConfig {
    /// Compression level, 0..=11. 5 is the datastar-go default — strong
    /// ratios at modest CPU.
    pub level: u32,
    /// log2 of the sliding window size, 10..=24. 18 ≈ 263 KB, Murphy's
    /// sweet spot for SSE: most of the ratio benefit, ~256 KB RAM/conn.
    pub lgwin: u32,
    /// Working buffer the encoder writes into between flushes.
    pub buffer_size: usize,
}

impl Default for BrotliSseConfig {
    fn default() -> Self {
        Self { level: 5, lgwin: 18, buffer_size: 4096 }
    }
}

/// Returns true if the request's `Accept-Encoding` header advertises `br`
/// with a non-zero q-value.
pub fn accepts_brotli(req: &HttpRequest) -> bool {
    req.headers()
        .get(header::ACCEPT_ENCODING)
        .and_then(|v| v.to_str().ok())
        .map(parse_accepts_br)
        .unwrap_or(false)
}

fn parse_accepts_br(header_value: &str) -> bool {
    for entry in header_value.split(',') {
        let mut parts = entry.split(';').map(str::trim);
        let coding = match parts.next() {
            Some(c) => c,
            None => continue,
        };
        if !coding.eq_ignore_ascii_case("br") {
            continue;
        }
        // Only reject if explicit q=0; everything else (including missing q) accepts.
        let rejected = parts.any(|p| {
            let mut kv = p.splitn(2, '=').map(str::trim);
            matches!((kv.next(), kv.next()), (Some("q"), Some(q)) if q.parse::<f32>().ok() == Some(0.0))
        });
        return !rejected;
    }
    false
}

/// Build an SSE response from a stream of pre-formatted SSE event strings
/// (each ending with the SSE event terminator `\n\n`). When the client
/// advertises `Accept-Encoding: br`, the body is brotli-compressed with
/// per-event flushes; otherwise it falls through to identity.
pub fn brotli_sse_response<S>(
    req: &HttpRequest,
    events: S,
    config: BrotliSseConfig,
) -> HttpResponse
where
    S: Stream<Item = String> + Unpin + 'static,
{
    let mut builder = HttpResponse::Ok();
    builder
        .content_type("text/event-stream")
        .insert_header((header::CACHE_CONTROL, HeaderValue::from_static("no-cache")))
        .insert_header(("X-Accel-Buffering", "no"));

    if accepts_brotli(req) {
        builder.insert_header((header::CONTENT_ENCODING, HeaderValue::from_static("br")));
        builder.streaming(brotli_compress_stream(events, config))
    } else {
        let identity = events.map(|e| Ok::<_, std::io::Error>(Bytes::from(e)));
        builder.streaming(identity)
    }
}

/// Wrap an SSE event stream so each `String` becomes a brotli-compressed
/// chunk emitted with `BROTLI_OPERATION_FLUSH`.
pub fn brotli_compress_stream<S>(
    events: S,
    config: BrotliSseConfig,
) -> impl Stream<Item = Result<Bytes, std::io::Error>>
where
    S: Stream<Item = String> + Unpin,
{
    async_stream::stream! {
        let sink = SharedBuf::default();
        let mut encoder = CompressorWriter::new(
            sink.clone(),
            config.buffer_size,
            config.level,
            config.lgwin,
        );
        let mut events = events;

        while let Some(event) = events.next().await {
            if let Err(e) = encoder.write_all(event.as_bytes()) {
                yield Err(e);
                return;
            }
            if let Err(e) = encoder.flush() {
                yield Err(e);
                return;
            }
            let chunk = sink.take();
            if !chunk.is_empty() {
                yield Ok(Bytes::from(chunk));
            }
        }

        // Drop runs BROTLI_OPERATION_FINISH and writes the trailing block.
        drop(encoder);
        let tail = sink.take();
        if !tail.is_empty() {
            yield Ok(Bytes::from(tail));
        }
    }
}

#[derive(Clone, Default)]
struct SharedBuf(Arc<Mutex<Vec<u8>>>);

impl SharedBuf {
    fn take(&self) -> Vec<u8> {
        std::mem::take(&mut *self.0.lock().expect("brotli sink mutex poisoned"))
    }
}

impl Write for SharedBuf {
    fn write(&mut self, data: &[u8]) -> std::io::Result<usize> {
        self.0
            .lock()
            .expect("brotli sink mutex poisoned")
            .extend_from_slice(data);
        Ok(data.len())
    }
    fn flush(&mut self) -> std::io::Result<()> {
        Ok(())
    }
}

/// Format a payload as a single SSE event with the given event name. Each
/// line of `data` becomes its own `data:` field, and the event is terminated
/// with a blank line. This mirrors what datastar-py emits.
pub fn format_sse_event(event_name: &str, data: &str) -> String {
    let mut s = String::with_capacity(data.len() + event_name.len() + 16);
    s.push_str("event: ");
    s.push_str(event_name);
    s.push('\n');
    for line in data.split('\n') {
        s.push_str("data: ");
        s.push_str(line);
        s.push('\n');
    }
    s.push('\n');
    s
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_accept_encoding_br() {
        assert!(parse_accepts_br("br"));
        assert!(parse_accepts_br("gzip, br"));
        assert!(parse_accepts_br("br;q=0.9, gzip"));
        assert!(parse_accepts_br("BR"));
        assert!(!parse_accepts_br("gzip, deflate"));
        assert!(!parse_accepts_br("br;q=0"));
        assert!(!parse_accepts_br(""));
    }

    #[test]
    fn formats_sse_event() {
        let s = format_sse_event("datastar-patch-elements", "<div>hi</div>");
        assert!(s.starts_with("event: datastar-patch-elements\n"));
        assert!(s.contains("data: <div>hi</div>\n"));
        assert!(s.ends_with("\n\n"));
    }

    #[test]
    fn defaults_match_datastar_go_reference() {
        let cfg = BrotliSseConfig::default();
        assert_eq!(cfg.level, 5);
        assert_eq!(cfg.lgwin, 18);
    }
}
