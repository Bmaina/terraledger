use std::env;
use std::net::SocketAddr;

use tokio::io::AsyncReadExt;
use tokio::net::TcpListener;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Render provides the port via $PORT, default to 8080 locally
    let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());
    let addr: SocketAddr = format!("0.0.0.0:{}", port).parse()?;

    let listener = TcpListener::bind(addr).await?;
    println!("TerraLedger is running on port {}", port);

    loop {
        let (mut socket, _) = listener.accept().await?;

        // This is the line that was causing the new error
        tokio::spawn(async move {
            let mut buffer = [0u8; 1024];

            // Read and ignore for now
            let _ = socket.read(&mut buffer).await;
        });
    }
}