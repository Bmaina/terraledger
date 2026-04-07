#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());
    let addr: SocketAddr = format!("0.0.0.0:{}", port).parse()?;

    let listener = TcpListener::bind(addr).await?;
    println!("TerraLedger is running on port {}", port);

    loop {
        let (mut socket, _) = listener.accept().await?;

        tokio::spawn(async move {
            let mut buffer = [0u8; 1024];

            // Simple HTTP response
            if let Ok(_) = socket.read(&mut buffer).await {
                let response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 23\r\n\r\nHello from TerraLedger!\n";
                let _ = socket.write_all(response.as_bytes()).await;
                let _ = socket.flush().await;
            }
        });
    }
}