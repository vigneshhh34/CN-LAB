# Name: [Your Name]
# Roll Number: [Your Roll Number]

import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

SERVER_IP = '172.17.228.8'
PORT = 9991

class ChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Socket Chat Client")
        self.root.geometry("550x550")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.client_socket = None
        self.username = None
        self.is_connected = False

        # --- GUI Layout ---
        # 1. Connection Frame
        conn_frame = tk.LabelFrame(root, text=" Connection ", padx=10, pady=10)
        conn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(conn_frame, text="Username:").pack(side=tk.LEFT)
        self.user_entry = tk.Entry(conn_frame, width=15)
        self.user_entry.pack(side=tk.LEFT, padx=5)

        self.connect_btn = tk.Button(conn_frame, text="Connect", command=self.connect_to_server, bg="lightgreen")
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        self.disconnect_btn = tk.Button(conn_frame, text="Disconnect", command=self.exit_chat, state=tk.DISABLED, bg="lightcoral")
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)

        # 2. Chat History Display Area
        chat_frame = tk.LabelFrame(root, text=" Live Chat Window ", padx=10, pady=10)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state='disabled', height=15)
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # 3. Actions / Functionalities Frame
        action_frame = tk.Frame(root, padx=10, pady=5)
        action_frame.pack(fill=tk.X, padx=10)

        self.users_btn = tk.Button(action_frame, text="Get Active Users (/users)", command=self.get_users, state=tk.DISABLED)
        self.users_btn.pack(fill=tk.X, pady=2)

        # 4. Messaging Frame (<user>:msg)
        msg_frame = tk.LabelFrame(root, text=" Send Message ", padx=10, pady=10)
        msg_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(msg_frame, text="Target User (or leave blank for broadcast):").grid(row=0, column=0, sticky='w')
        self.target_entry = tk.Entry(msg_frame, width=20)
        self.target_entry.grid(row=0, column=1, padx=5, pady=2, sticky='w')

        tk.Label(msg_frame, text="Message:").grid(row=1, column=0, sticky='w')
        self.msg_entry = tk.Entry(msg_frame, width=35)
        self.msg_entry.grid(row=1, column=1, padx=5, pady=2, sticky='w')
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        btn_box = tk.Frame(msg_frame)
        btn_box.grid(row=2, column=0, columnspan=2, pady=5)

        self.send_priv_btn = tk.Button(btn_box, text="Send Private", command=self.send_message, state=tk.DISABLED, bg="lightblue")
        self.send_priv_btn.pack(side=tk.LEFT, padx=5)

        self.broadcast_btn = tk.Button(btn_box, text="Broadcast All", command=self.broadcast_message, state=tk.DISABLED, bg="plum")
        self.broadcast_btn.pack(side=tk.LEFT, padx=5)

    def append_chat(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def connect_to_server(self):
        uname = self.user_entry.get().strip()
        if not uname:
            messagebox.showerror("Error", "Please enter a valid username.")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_IP, PORT))

            # Send username to server
            self.client_socket.sendall(uname.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')

            if response.startswith("REJECTED"):
                messagebox.showerror("Rejected", response)
                self.client_socket.close()
                return

            self.username = uname
            self.is_connected = True
            
            # Toggle Button states
            self.user_entry.config(state=tk.DISABLED)
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.users_btn.config(state=tk.NORMAL)
            self.send_priv_btn.config(state=tk.NORMAL)
            self.broadcast_btn.config(state=tk.NORMAL)

            self.append_chat(f"[*] Successfully connected as '{self.username}'")

            # Start background thread to listen for incoming messages
            threading.Thread(target=self.receive_messages, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def receive_messages(self):
        while self.is_connected:
            try:
                data = self.client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                if data.startswith("ONLINE_USERS:"):
                    users = data.split(":", 1)[1]
                    self.append_chat(f"\n[Active Users Online]: {users}\n")
                else:
                    self.append_chat(data)
            except:
                break

    def get_users(self):
        if self.is_connected:
            try:
                self.client_socket.sendall("/users".encode('utf-8'))
            except:
                pass

    def send_message(self):
        if not self.is_connected:
            return
        target = self.target_entry.get().strip()
        msg = self.msg_entry.get().strip()

        if not msg:
            return

        if target:
            # Format: <user1>:msg
            payload = f"{target}:{msg}"
            self.append_chat(f"You -> {target}: {msg}")
        else:
            # If target is blank, default to broadcast
            self.broadcast_message()
            return

        try:
            self.client_socket.sendall(payload.encode('utf-8'))
            self.msg_entry.delete(0, tk.END)
        except:
            messagebox.showerror("Error", "Failed to send message.")

    def broadcast_message(self):
        if not self.is_connected:
            return
        msg = self.msg_entry.get().strip()
        if not msg:
            return

        # Format: <broadcast>:msg
        payload = f"<broadcast>:{msg}"
        self.append_chat(f"You (Broadcast): {msg}")

        try:
            self.client_socket.sendall(payload.encode('utf-8'))
            self.msg_entry.delete(0, tk.END)
        except:
            messagebox.showerror("Error", "Failed to broadcast message.")

    def exit_chat(self):
        if self.is_connected:
            try:
                self.client_socket.sendall("/exit".encode('utf-8'))
            except:
                pass
            self.is_connected = False
            try:
                self.client_socket.close()
            except:
                pass

        self.root.quit()

    def on_closing(self):
        self.exit_chat()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()