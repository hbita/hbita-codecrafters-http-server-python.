import socket  # noqa: F401


def main():
    print("Logs from your program will appear here!")

    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()
    data = connection.recv(1024).decode()
    request_line = data.split("\n\r")[0]
    method,path ,_ =request_line.split(" ",2)
    if path.startswith("/echo/"):
         response_str = path.split("/echo/")[1]
         response_headers = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_str)}\r\n"
            "\r\n")
         response_body = response_str
         response = (response_headers + response_body)
    elif path == "/":
         response="HTTP/1.1 200 OK\r\n\r\n"
    else :
         response = "HTTP/1.1 404 Not Found\r\n\r\n"
    connection.sendall(response.encode())
if __name__ == "__main__":
    main()
