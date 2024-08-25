import tkinter as tk
from tkinter import messagebox
import chess
import chess.svg

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Learn to Play Chess")
        
        self.board = chess.Board()

        self.canvas = tk.Canvas(root, width=480, height=480)
        self.canvas.pack()

        self.instruction_label = tk.Label(root, text="Welcome to Chess! Make your first move.", font=('Arial', 14))
        self.instruction_label.pack(pady=10)

        self.move_entry = tk.Entry(root, font=('Arial', 14))
        self.move_entry.pack(pady=5)

        self.move_button = tk.Button(root, text="Make Move", command=self.make_move, font=('Arial', 14))
        self.move_button.pack(pady=5)

        self.reset_button = tk.Button(root, text="Reset Game", command=self.reset_game, font=('Arial', 14))
        self.reset_button.pack(pady=5)

        self.draw_board()

    def draw_board(self):
        board_svg = chess.svg.board(self.board).encode("utf-8")
        self.board_image = tk.PhotoImage(data=board_svg)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.board_image)

    def make_move(self):
        move = self.move_entry.get()
        try:
            self.board.push_san(move)
            self.draw_board()
            self.instruction_label.config(text="Move made! Now it's the opponent's turn.")
        except ValueError:
            messagebox.showerror("Invalid Move", "That move is not valid. Try again!")

    def reset_game(self):
        self.board.reset()
        self.draw_board()
        self.instruction_label.config(text="Game reset! Make your first move.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()
