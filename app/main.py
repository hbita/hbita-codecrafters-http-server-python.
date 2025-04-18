import socket
import threading 
import argparse 
import os

def handle_client(connection, directory):
    try:
        data = connection.recv(1024)
        if not data:
            return

        request_line = data.split(b"\r\n")[0]
        parts = request_line.split(b' ')
        
        if len(parts) < 3:
            response = b"HTTP/1.1 400 Bad Request\r\n\r\n"
            connection.sendall(response)
            return
        method = parts[0].decode().upper()
        path = parts[1].decode()
        headers = parse_header(data)

        if path.startswith("/echo/"):
            response_str = path.split("/echo/")[1]
            # Check Accept-Encoding for gzip support
            accept_encoding = headers.get('accept-encoding', '')
            encodings = [e.strip().lower() for e in accept_encoding.split(',')]
            content_encoding = 'Content-Encoding: gzip\r\n' if 'gzip' in encodings else ''
            
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/plain\r\n"
                f"{content_encoding}"
                f"Content-Length: {len(response_str)}\r\n"
                f"\r\n{response_str}"
            )
            connection.sendall(response.encode())
        elif path == "/":
            response = b"HTTP/1.1 200 OK\r\n\r\n"
            connection.sendall(response)
        elif path == "/user-agent":
            user_agent = headers.get('user-agent', '')
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(user_agent)}\r\n"
                f"\r\n{user_agent}")
            connection.sendall(response.encode())
        elif path.startswith("/files/"):
            filename = os.path.basename(path.split("/files/")[1])
            if directory:
                filepath = os.path.join(directory, filename)
                if method == "GET":
                    if os.path.isfile(filepath):
                        with open(filepath, 'rb') as f:
                            content = f.read()
                            content_length = f"Content-Length: {len(content)}\r\n".encode()
                            headers = (
                                b"HTTP/1.1 200 OK\r\n"
                                b"Content-Type: application/octet-stream\r\n"
                                + content_length +
                                b"\r\n"
                            )
                            connection.sendall(headers + content)
                    else:
                        response = b"HTTP/1.1 404 Not Found\r\n\r\n"
                        connection.sendall(response)
                elif method == "POST":
                    if 'content-length' not in headers:
                        response = b"HTTP/1.1 400 Bad Request\r\n\r\n"
                        connection.sendall(response)
                        return
                    header_body_split = data.split(b"\r\n\r\n", 1)
                    if len(header_body_split) < 2:
                        response = b"HTTP/1.1 400 Bad Request\r\n\r\n"
                        connection.sendall(response)
                        return
                    body = header_body_split[1]
                    content_length = int(headers.get("content-length", 0))
                    body = body[:content_length]
                    with open(filepath, 'wb') as f:
                        f.write(body)
                        response = b"HTTP/1.1 201 Created\r\n\r\n"
                        connection.sendall(response)
                else:
                    response = (
                        b"HTTP/1.1 405 Method Not Allowed\r\n"
                        b"Allow: GET, POST\r\n\r\n"
                    )
                    connection.sendall(response)
            else:
                response = b"HTTP/1.1 405 Method Not Allowed\r\n\r\n"
                connection.sendall(response)
        else:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"
            connection.sendall(response)
    finally:
        connection.close()

def parse_header(data):
    headers = {}
    lines = data.split(b"\r\n")[1:]
    for line in lines:
        if not line:
            break
        try:
            key, value = line.split(b":", 1)
            headers[key.decode().lower()] = value.strip().decode()
        except ValueError:
            continue
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
            thread = threading.Thread(target=handle_client, args=(connection, args.directory))
            thread.start()
    except KeyboardInterrupt:
        server_socket.close()

if __name__ == "__main__":
    main()