tokio::spawn(async move {
    let mut buffer = [0u8; 1024];

    match socket.read(&mut buffer).await {
        Ok(n) if n == 0 => {
            // Client disconnected
        }
        Ok(n) => {
            println!("Read {} bytes", n);
            // TODO: process the data in buffer[..n]
        }
        Err(e) => {
            eprintln!("Read error: {}", e);
        }
    }
});