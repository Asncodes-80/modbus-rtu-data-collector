use std::time::Duration;

use tokio_modbus::client::rtu;
use tokio_modbus::prelude::*;
use tokio_serial::SerialStream;

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Rust RTU Program Started");
    let tty_path = "/dev/tty";
    let slave = Slave(0x01);

    // RTU connection
    let port = match tokio_serial::new(tty_path, 9600)
        .timeout(Duration::from_secs(1))
        .open()
    {
        Ok(p) => SerialStream::open(p)?,
        Err(e) => {
            println!("Failed to open serial port: {}", e);
            return Ok(()); // Early exit if port can't be opened
        }
    };

    let mut ctx = rtu::connect(SerialStream::open(&port).unwrap()).await?;
    ctx.set_slave(slave);
    let response = ctx.read_holding_registers(0x000, 5).await?;

    println!("Received data {:?}", response);

    Ok(())
}
