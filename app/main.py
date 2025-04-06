import socket  # noqa: F401


def main():
    print("Logs from your program will appear here!")

    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()
    data = connection.recv(1024).decode()
    request_line = data.split("\n\r")[0]
    path=request_line.split(" ")[1]
    if path == '/':
         response = "HTTP/1.1 200 OK\r\n\r\n"
    else :
         response = "HTTP/1.1 404 Not Found\r\n\r\n"
    connection.sendall(response.encode())
if __name__ == "__main__":
    main()
