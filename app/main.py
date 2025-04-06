import socket  # noqa: F401
import threading

def handle_client(connection):
     try:
         data = connection.recv(1024).decode()
         if not data :
              return
         request_line = data.split("\n\r")[0]
         parts= request_line.split(' ')
         if len(parts) < 3:
              response = "HTTP/1.1 404 Not Found\r\n\r\n"
              connection.sendall(response.encode())
              return
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
         connection.sendall(response.encode()) 
     finally :
          connection.close()   
def parse_header(data):
     headers={}
     lines =data.split("\r\n")[1:]
     for line in lines :
          if not line :
               break
          key ,value =line.split(":",1)
          headers[key]=value.strip()
     return headers
def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    try :
         while True :
             connection, _= server_socket.accept()
             thread = threading.Thread(target=handle_client, args=(connection,))
             thread.start()
    except KeyboardInterrupt:
        server_socket.close()
    
if __name__ == "__main__":
    main()
