use std::{thread, time::Duration, fs::File, io::Read, process::{self, Command}};
use serde::Deserialize;
use serde_json::Value;

const BROWSER_COMMAND: &str = if cfg!(target_os = "windows") {"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"} else {"open"};
const SERVER_COMMAND: &str = if cfg!(target_os = "windows") {"src/server.exe"} else {"src/server"};

fn read_json(filename: &str) -> Value {
    println!("Reading json file: {}", filename);
    let mut f: File = File::open(filename)
        .expect("Failed to open file");

    let mut contents = String::new();
    f.read_to_string(&mut contents)
        .expect("Failed to read file");

    let v: Value = serde_json::from_str(&contents).unwrap();

    v
}

fn start_go_server() {
    let mut request_addresses = read_json(".\\src\\settings.json")["server"].to_string().replace(r#"{"listen":"#, "");
    request_addresses.pop();
    #[derive(Deserialize)]
    struct RequestAddress {
        hostname: String,
        port: i32,
    }

    let deserialized_request_addresses: Vec<RequestAddress> = serde_json::from_str(&request_addresses).unwrap();
    let __using_address: Vec<String> = String::from_utf8_lossy(&Command::new("netstat").arg("-nao").output().expect("Failed to check using_address").stdout).lines().fold(Vec::new(), |mut s, i| {s.push(i.to_string());s});
    
    for request_address in deserialized_request_addresses {
        let req = request_address.hostname.to_string()+ ":" + &request_address.port.to_string();

        if cfg!(target_os = "windows") {
            for (i, __process) in __using_address.iter().enumerate() {
                let process = __process.split_whitespace()
                    .fold(Vec::new(), |mut s, i| {
                        s.push(i.to_string());
                        s
                    });
                    if process.len() > 4 && i > 3{
                        let pid: u32 = process[4].parse().unwrap();
                    if pid > 100 {
                        let ip = process[2].as_str();
                        if ip == req {
                            println!("ip: {}, pid: {}", ip, process[4]);
                            Command::new("taskkill")
                                .args(&["/f", "/pid", process[4].as_str()])
                                .spawn()
                                .expect("Failed to execute taskkill");
                            };
                        };
                    };
                };
        }
    

        thread::spawn(move || {
            let mut go_server = Command::new(SERVER_COMMAND)
                .current_dir(".\\src\\")
                .args(["-h", &request_address.hostname, "-p", &request_address.port.to_string()])
                .spawn()
                .expect("Failed to start go server");

            match go_server.try_wait() {
                Ok(Some(status)) => println!("exited with: {}", status),
                Ok(None) => {
                    let res = go_server.wait();
                    println!("result: {res:?}");
                    process::exit(0);
                    },
                Err(_e) => process::exit(500),
            };
        });
        thread::sleep(Duration::from_millis(10));
        let open_url = String::new()+"--app=https://"+&req;
        Command::new(BROWSER_COMMAND)
            .arg(open_url)
            .spawn()
            .expect("Failed to start Google Chrome");
    };
}

fn main() {
    start_go_server();
    loop {
        thread::sleep(Duration::from_secs(30));
    };
}