import socket
import threading 
import argparse 
import os

def handle_client(connection,directory):
    try:
        data = connection.recv(1024).decode()
        if not data:
            return

        request_line = data.split("\r\n")[0]  
        parts = request_line.split(' ')
        
        if len(parts) < 3:
            response = "HTTP/1.1 400 Bad Request\r\n\r\n"
            connection.sendall(response.encode())
            return

        _, path, _ = parts
        headers = parse_header(data)

        if path.startswith("/echo/"):
            response_str = path.split("/echo/")[1]
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(response_str)}\r\n"
                f"\r\n{response_str}"
            )
        elif path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif path == "/user-agent":
            user_agent = headers.get('User-Agent', '')
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(user_agent)}\r\n"
                f"\r\n{user_agent}")
        elif path.startswitch("/files/") :
            filename=path.split("files/")[1]
            if directory :
                filepath =os.path.join(directory,filename)
                if os.path.isfile(filepath) :
                    with open(filepath ,'rb') as f :
                        content=f.read()
                    headers = (
                        "HTTP/1.1 200 OK\r\n"
                        f"Content-Type: application/octet-stream\r\n"
                        f"Content-Length: {len(content)}\r\n"
                        "\r\n"
                    )
                    headers_bytes = headers.encode()
                    connection.sendall(headers_bytes + content)
                    return
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
        else:  
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

        connection.sendall(response.encode())
    finally:
        connection.close()

def parse_header(data):
    headers = {}
    lines = data.split("\r\n")[1:]
    for line in lines:
        if not line:
            break
        key, value = line.split(":", 1)
        headers[key] = value.strip()
    return headers

def main():
    print("Logs from your program will appear here!")
    parser = argparse.ArgumentParser() 
    parser.add_argument('--directory', type=str)  
    args, _ = parser.parse_known_args() 
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    try:
        while True:
            connection, _ = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(connection,args.directory))
            thread.start()
    except KeyboardInterrupt:
        server_socket.close()

if __name__ == "__main__":
    main()