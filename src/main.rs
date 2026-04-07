use std::env;
use std::net::SocketAddr;

use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Render sets the PORT environment variable automatically
    let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());
    let addr: SocketAddr = format!("0.0.0.0:{}", port).parse()?;

    let listener = TcpListener::bind(addr).await?;
    println!("✅ TerraLedger HTTP server is running on http://0.0.0.0:{}", port);
    println!("🌐 Visit: https://{}.onrender.com", /* your service name */);

    loop {
        let (mut socket, addr) = listener.accept().await?;
        println!("📥 New connection from: {}", addr);

        tokio::spawn(async move {
            let mut buffer = [0u8; 1024];

            // Read the incoming request
            match socket.read(&mut buffer).await {
                Ok(0) => {
                    println!("❌ Client disconnected ({} bytes read)", 0);
                }
                Ok(n) => {
                    let request = String::from_utf8_lossy(&buffer[..n]);
                    println!("📨 Received {} bytes from {}:\n{}", n, addr, request);

                    // Simple but valid HTTP response
                    let response = "HTTP/1.1 200 OK\r\n\
                                   Content-Type: text/plain\r\n\
                                   Content-Length: 48\r\n\
                                   Connection: close\r\n\
                                   \r\n\
                                   Hello from TerraLedger! 👋\n\
                                   You sent a request to the server.\n";

                    if let Err(e) = socket.write_all(response.as_bytes()).await {
                        eprintln!("❌ Failed to write response: {}", e);
                    }
                    let _ = socket.flush().await;
                    println!("✅ Response sent to {}", addr);
                }
                Err(e) => {
                    eprintln!("❌ Read error from {}: {}", addr, e);
                }
            }
        });
    }
}