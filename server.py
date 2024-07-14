import socket
import threading
import time

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen()

    def client_handler(self, client_socket):
        userid = None
        try:
            userid_message = client_socket.recv(1024).decode()
            if userid_message:
                userid = userid_message.split(" ")[0]  # 假設消息格式是 "userid 加入了聊天室"
                print(f"{userid_message} - Connected")
                self.broadcast(userid_message, client_socket)
                time.sleep(0.001)
                self.update_online_count()

            while True:
                message = client_socket.recv(1024).decode()
                if message:
                    self.broadcast(message, client_socket)
                    if message == f"{userid} 離開了聊天室":
                        break
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if userid:
                leave_message = f"{userid} 離開了聊天室"
                print(leave_message)  # 打印離開消息
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            time.sleep(0.001)
            self.update_online_count()

    def update_online_count(self):
        count_message = f"在線人數: {len(self.clients)}"
        for client_socket in self.clients:
            try:
                client_socket.send(count_message.encode())
            except Exception as e:
                print(f"Error: {e}")
                client_socket.close()
                self.clients.remove(client_socket)

    def broadcast(self, message, source_socket):
        for client_socket in self.clients:
            if client_socket != source_socket:
                try:
                    client_socket.send(message.encode())
                except Exception as e:
                    print(f"Error: {e}")
                    client_socket.close()
                    self.clients.remove(client_socket)

    def run(self):
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.clients.append(client_socket)
            client_thread = threading.Thread(target=self.client_handler, args=(client_socket,))
            client_thread.start()

if __name__ == "__main__":
    server = ChatServer('localhost', 7000)
    server.run()
