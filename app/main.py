import socket
import threading
import argparse
import os
import gzip

def handle_client(connection, directory):
    buffer = b''
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            
            buffer += data

            while True:
                headers_end = buffer.find(b'\r\n\r\n')
                if headers_end == -1:
                    break

                headers_part = buffer[:headers_end]
                headers = parse_header(headers_part)
                content_length = int(headers.get('content-length', 0))
                
                total_request_size = headers_end + 4 + content_length
                if len(buffer) < total_request_size:
                    break

                request_data = buffer[:total_request_size]
                buffer = buffer[total_request_size:]

                response = process_request(request_data, directory)
                if response:
                    connection.sendall(response)

                if headers.get('connection', '').lower() == 'close':
                    connection.close()
                    return

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        connection.close()

def process_request(request_data, directory):
    try:
        request_line = request_data.split(b"\r\n")[0]
        parts = request_line.split(b' ')
        
        if len(parts) < 3:
            return b"HTTP/1.1 400 Bad Request\r\n\r\n"

        method = parts[0].decode().upper()
        path = parts[1].decode()
        headers = parse_header(request_data)
        body = request_data.split(b'\r\n\r\n', 1)[1] if b'\r\n\r\n' in request_data else b''

        if path.startswith("/echo/"):
            return handle_echo(path, headers)
        elif path == "/":
            return handle_root(headers)
        elif path == "/user-agent":
            return handle_user_agent(headers)
        elif path.startswith("/files/"):
            return handle_files(path, method, headers, body, directory)
        else:
            return handle_not_found(headers)

    except Exception as e:
        print(f"Processing error: {e}")
        return b"HTTP/1.1 500 Internal Server Error\r\n\r\n"

def handle_echo(path, headers):
    response_str = path.split("/echo/", 1)[1]
    accept_encoding = headers.get('accept-encoding', '')
    encodings = [e.strip().lower() for e in accept_encoding.split(',')]
    
    connection_header = b"Connection: close\r\n" if headers.get('connection', '').lower() == 'close' else b""
    
    if 'gzip' in encodings:
        compressed_body = gzip.compress(response_str.encode())
        content_encoding = b"Content-Encoding: gzip\r\n"
        content_length = len(compressed_body)
        body = compressed_body
    else:
        body = response_str.encode()
        content_encoding = b""
        content_length = len(body)

    return (
        b"HTTP/1.1 200 OK\r\n"
        + connection_header +
        b"Content-Type: text/plain\r\n"
        + content_encoding +
        f"Content-Length: {content_length}\r\n\r\n".encode()
    ) + body

def handle_root(headers):
    connection_header = b"Connection: close\r\n" if headers.get('connection', '').lower() == 'close' else b""
    return b"HTTP/1.1 200 OK\r\n" + connection_header + b"\r\n"

def handle_user_agent(headers):
    user_agent = headers.get('user-agent', '')
    connection_header = "Connection: close\r\n" if headers.get('connection', '').lower() == 'close' else ""
    return (
        f"HTTP/1.1 200 OK\r\n"
        f"{connection_header}"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(user_agent)}\r\n\r\n"
        f"{user_agent}"
    ).encode()

def handle_files(path, method, headers, body, directory):
    if not directory:
        return b"HTTP/1.1 405 Method Not Allowed\r\n\r\n"

    filename = os.path.basename(path.split("/files/", 1)[1])
    filepath = os.path.join(directory, filename)
    connection_header = b"Connection: close\r\n" if headers.get('connection', '').lower() == 'close' else b""

    if method == "GET":
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                content = f.read()
                return (
                    b"HTTP/1.1 200 OK\r\n"
                    + connection_header +
                    b"Content-Type: application/octet-stream\r\n"
                    f"Content-Length: {len(content)}\r\n\r\n".encode()
                    + content
                )
        else:
            return b"HTTP/1.1 404 Not Found\r\n\r\n"
    elif method == "POST":
        content_length = int(headers.get('content-length', 0))
        if content_length == 0:
            return b"HTTP/1.1 400 Bad Request\r\n\r\n"

        with open(filepath, 'wb') as f:
            f.write(body[:content_length])
        return b"HTTP/1.1 201 Created\r\n" + connection_header + b"\r\n"
    else:
        return (
            b"HTTP/1.1 405 Method Not Allowed\r\n"
            + connection_header +
            b"Allow: GET, POST\r\n\r\n"
        )

def handle_not_found(headers):
    connection_header = b"Connection: close\r\n" if headers.get('connection', '').lower() == 'close' else b""
    return b"HTTP/1.1 404 Not Found\r\n" + connection_header + b"\r\n"

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
    args = parser.parse_args()
    
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