import socket
import threading
import select
import sys
import tkinter as tk
from tkinter import simpledialog

class ChatClient:
    def __init__(self, host, port, userid):
        self.host = host
        self.port = port
        self.userid = userid
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.send(f"{userid} 加入了聊天室".encode())
        self.socket.setblocking(False)

    def setup_gui(self):
        self.window = tk.Tk()
        self.window.title(f"聊天室 - {self.userid}")
        
        # 在右上角添加用於顯示在線人數的標籤
        self.online_count_label = tk.Label(self.window, text="在線人數: 0")
        self.online_count_label.pack(side=tk.TOP, anchor='ne', padx=5, pady=5)
        
        # 配置聊天文字區域
        self.chat_text = tk.Text(self.window, state='disabled', height=15, width=50)
        self.chat_text.pack(padx=5, pady=5, expand=True, fill=tk.BOTH)

        # 配置消息輸入框
        self.msg_entry = tk.Entry(self.window)
        self.msg_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.msg_entry.bind("<Return>", self.on_enter_pressed)

        # 添加傳送按鈕
        self.send_button = tk.Button(self.window, text="傳送", command=self.on_send_pressed)
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_close(self):
        # 當窗口關閉時發送離開消息
        try:
            self.socket.send(f"{self.userid} 離開了聊天室".encode())
            self.socket.close()
        except Exception as e:
            print(f"Error sending leave message: {e}")
        finally:
            self.window.destroy()  # 關閉窗口
            
    def on_enter_pressed(self, event):
        self.send_message()

    def on_send_pressed(self):
        self.send_message()

    def send_message(self):
        message = self.msg_entry.get()
        if message:
            self.socket.send(f"{self.userid}: {message}".encode())
            self.update_chat_window(f"{self.userid}: {message}")
            self.msg_entry.delete(0, tk.END)
        
    def update_chat_window(self, message): 
        if message.startswith("在線人數:"):
            # 更新在線人數標籤
            self.online_count_label.config(text=message)
        else:
            self.chat_text.config(state='normal')
            self.chat_text.insert(tk.END, message + '\n')
            self.chat_text.config(state='disabled')
            self.chat_text.see(tk.END)

    def receive_messages(self):
        while True:
            read_sockets, _, _ = select.select([self.socket], [], [], 0.1) # non blocking
            for sock in read_sockets:
                try:
                    message = sock.recv(1024).decode()
                    if message:
                        self.update_chat_window(message)
                except Exception as e:
                    print(f"Error: {e}")
                    sys.exit()

    def run(self):
        self.setup_gui()
        threading.Thread(target=self.receive_messages).start()
        self.window.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隱藏主窗口
    userid = simpledialog.askstring("用戶ID", "請輸入您的用戶ID:", parent=root)
    if userid:
        client = ChatClient('localhost', 7000, userid)
        client.run()
    root.mainloop()