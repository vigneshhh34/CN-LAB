import socket, threading, queue
import tkinter as tk

# 1. socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 5000))
q = queue.Queue()

# 2. background thread: only receives, puts into queue
def receive():
    while True:
        data = sock.recv(1024)
        if not data:
            break
        q.put(data.decode())

threading.Thread(target=receive, daemon=True).start()

# 3. GUI
root = tk.Tk()
root.title("Chat")

text = tk.Text(root, height=15, width=40, state="disabled")
text.pack()

entry = tk.Entry(root, width=30)
entry.pack(side="left")

def send():                                # called by button click
    msg = entry.get()
    if msg:
        sock.sendall(msg.encode())
        entry.delete(0, tk.END)

tk.Button(root, text="Send", command=send).pack(side="left")

# 4. main thread: checks queue every 100 ms and updates the GUI
def check_queue():
    while not q.empty():
        msg = q.get()
        text.config(state="normal")
        text.insert(tk.END, msg + "\n")
        text.config(state="disabled")
    root.after(100, check_queue)           # schedule itself again

check_queue()
root.mainloop()

