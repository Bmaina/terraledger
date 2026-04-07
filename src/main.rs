use tokio::net::TcpListener;

#[tokio::main]
async fn main() {
    // Get the port Render expects, default to 8080 locally
    let port = env::var("PORT").unwrap_or("8080".to_string());
    let addr: SocketAddr = format!("0.0.0.0:{}", port).parse().unwrap();

    // Bind a TCP listener to the port
    let listener = TcpListener::bind(addr).await.unwrap();
    println!("TerraLedger is running on port {}", port);

    // Keep the app running
    loop {
        let (socket, _) = listener.accept().await.unwrap();
        tokio::spawn(async move {
            // For now, we just accept connections but do nothing
            drop(socket);
        });
    }
}