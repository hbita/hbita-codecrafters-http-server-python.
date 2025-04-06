import socket  # noqa: F401

def parse_header(data):
     headers={}
     lines =data.split("\r\n")[1:]
     for line in lines :
          if not line :
               break
          key ,value =line.split(":",1)
          headers[key]=value
     return headers

def main():
    print("Logs from your program will appear here!")

    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()
    data = connection.recv(1024).decode()
    request_line = data.split("\n\r")[0]
    method,path ,_ =request_line.split(" ",2)
    headers =parse_header(data)
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
    elif path =="/user-agent" :
          user_agent = headers.get('User-Agent','')
          response = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: text/plain\r\n"
            f"Content-Length: {len(user_agent)}\r\n"
            f"\r\n{user_agent}")
    else :
         response = "HTTP/1.1 404 Not Found\r\n\r\n"
    connection.sendall(response.encode())
if __name__ == "__main__":
    main()
