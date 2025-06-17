import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

# Configuration for local testing
HOST = '127.0.0.1'
PORT = 12345

# === MAIN GAME CLASS ===
class TicTacToe:
    def __init__(self, root, conn, is_server):
        self.root = root
        self.conn = conn              # Connection between two nodes (distributed)
        self.is_server = is_server    # Node autonomy: each decides role independently
        self.my_turn = is_server      # First move by server (distributed coordination)
        self.symbol = 'X' if is_server else 'O'
        self.opponent_symbol = 'O' if is_server else 'X'
        self.board = [''] * 9         # Shared distributed state of the game
        self.buttons = []
        self.game_over = False

        # === GUI Setup ===
        root.title(f"TicTacToe - You are '{self.symbol}'")
        root.configure(bg="#2c3e50")
        root.geometry("400x500")  # Visual UI

        self.status_label = tk.Label(root, text="", font=("Helvetica", 18, "bold"), fg="#ecf0f1", bg="#2c3e50")
        self.status_label.pack(pady=15)

        frame = tk.Frame(root, bg="#2c3e50")
        frame.pack()

        for i in range(9):
            btn = tk.Button(frame, text='', font=("Helvetica", 28, "bold"), width=4, height=2,
                            bg="#34495e", fg="#ecf0f1", activebackground="#2980b9",
                            activeforeground="white", bd=0,
                            command=lambda i=i: self.click(i))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.buttons.append(btn)

        self.restart_btn = tk.Button(root, text="Restart", font=("Helvetica", 14, "bold"),
                                     bg="#27ae60", fg="white", activebackground="#2ecc71",
                                     activeforeground="white", bd=0,
                                     command=self.restart, state=tk.DISABLED)
        self.restart_btn.pack(pady=20, ipadx=20, ipady=10)

        self.update_status()

        # Starts a background thread for real-time updates (live distributed communication)
        threading.Thread(target=self.receive_loop, daemon=True).start()

    def click(self, index):
        # Player can only play on their turn and on empty cells
        if not self.my_turn or self.game_over or self.board[index] != '':
            return
        self.make_move(index, self.symbol)
        self.send_move(index)  # Send move to opponent (shared distributed state update)
        self.my_turn = False
        self.update_status()

        # Check game status after move
        if self.check_winner(self.symbol):
            self.game_over = True
            self.status_label.config(text="🎉 You won!")
            self.restart_btn.config(state=tk.NORMAL)
        elif all(self.board):
            self.game_over = True
            self.status_label.config(text="🤝 Draw!")
            self.restart_btn.config(state=tk.NORMAL)

    def make_move(self, index, symbol):
        # Update local board (shared state)
        self.board[index] = symbol
        self.buttons[index].config(text=symbol, state=tk.DISABLED)
        self.buttons[index].config(fg="#e74c3c" if symbol == 'X' else "#f1c40f")

    def send_move(self, index):
        # Real-time data transfer to remote node (network-based message passing)
        try:
            self.conn.send(f"MOVE:{index}".encode())
        except:
            self.handle_disconnect()

    def receive_loop(self):
        # Always listening for incoming moves or restarts from other node
        while True:
            try:
                data = self.conn.recv(1024)
                if not data:
                    raise ConnectionResetError
                msg = data.decode()
                if msg.startswith("MOVE:"):
                    index = int(msg.split(':')[1])
                    self.root.after(0, self.opponent_move, index)
                elif msg == "RESTART":
                    self.root.after(0, self.restart_game)
            except:
                self.root.after(0, self.handle_disconnect)
                break

    def opponent_move(self, index):
        # Remote move handler — shared state updated across nodes
        if self.game_over:
            return
        self.make_move(index, self.opponent_symbol)
        if self.check_winner(self.opponent_symbol):
            self.game_over = True
            self.status_label.config(text="😞 You lost!")
            self.restart_btn.config(state=tk.NORMAL)
        elif all(self.board):
            self.game_over = True
            self.status_label.config(text="🤝 Draw!")
            self.restart_btn.config(state=tk.NORMAL)
        else:
            self.my_turn = True
            self.update_status()

    def check_winner(self, s):
        # Win conditions over distributed shared state
        wins = [(0,1,2),(3,4,5),(6,7,8),
                (0,3,6),(1,4,7),(2,5,8),
                (0,4,8),(2,4,6)]
        for a,b,c in wins:
            if self.board[a] == s and self.board[b] == s and self.board[c] == s:
                for idx in (a,b,c):
                    self.buttons[idx].config(bg="#16a085")
                return True
        return False

    def update_status(self):
        # UI feedback per distributed state
        if self.game_over:
            return
        self.status_label.config(text="🔵 Your turn" if self.my_turn else "⚪ Opponent's turn")

    def restart(self):
        # Restarting shared state
        try:
            self.conn.send("RESTART".encode())
        except:
            self.handle_disconnect()
        self.restart_game()

    def restart_game(self):
        # Resets game state
        self.board = ['']*9
        for btn in self.buttons:
            btn.config(text='', state=tk.NORMAL, bg="#34495e", fg="#ecf0f1")
        self.game_over = False
        self.restart_btn.config(state=tk.DISABLED)
        self.my_turn = self.is_server
        self.update_status()

    def handle_disconnect(self):
        # Fault-tolerance: detect node crash and continue operation
        self.game_over = True
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)
        self.status_label.config(text="❌ Opponent disconnected.")
        self.restart_btn.config(state=tk.DISABLED)
        messagebox.showwarning("Disconnected", "Opponent has disconnected. You win by default!")

# === SERVER NODE ===
def start_server():
    # One autonomous node binds and listens
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Waiting for connection on {HOST}:{PORT} ...")
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    return conn

# === CLIENT NODE ===
def start_client():
    # Another autonomous node connects
    ip = simpledialog.askstring("Connect", "Enter server IP:", initialvalue="127.0.0.1")
    if not ip:
        messagebox.showerror("Error", "IP is required")
        exit()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, PORT))
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect: {e}")
        exit()
    return s

# === MAIN ENTRY POINT ===
def main():
    root = tk.Tk()
    root.withdraw()  # Hide window initially
    mode = simpledialog.askstring("Mode", "Type 'server' to host, 'client' to join:")
    if not mode:
        return
    mode = mode.lower()
    if mode == 'server':
        conn = start_server()
        root.deiconify()
        TicTacToe(root, conn, is_server=True)
        root.mainloop()
    elif mode == 'client':
        conn = start_client()
        root.deiconify()
        TicTacToe(root, conn, is_server=False)
        root.mainloop()
    else:
        messagebox.showerror("Error", "Invalid input. Use 'server' or 'client'.")

# === RUN THE APP ===
if __name__ == "__main__":
    main()
