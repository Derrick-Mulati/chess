import tkinter as tk
from tkinter import messagebox

class ChessTutorialGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Tutorial")
        self.board = self.create_board()
        self.pieces = {
            "P": "Pawn",
            "R": "Rook",
            "N": "Knight",
            "B": "Bishop",
            "Q": "Queen",
            "K": "King"
        }
        self.create_widgets()

    def create_board(self):
        return [
            ["R", "N", "B", "Q", "K", "B", "N", "R"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["r", "n", "b", "q", "k", "b", "n", "r"]
        ]

    def create_widgets(self):
        self.board_frame = tk.Frame(self.root)
        self.board_frame.grid(row=0, column=0, padx=10, pady=10)

        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.grid(row=1, column=0, padx=10, pady=10)

        self.display_board()
        self.create_buttons()

    def display_board(self):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                color = "white" if (r + c) % 2 == 0 else "gray"
                label = tk.Label(self.board_frame, text=piece, width=4, height=2, bg=color, font=("Helvetica", 16))
                label.grid(row=r, column=c)

    def show_piece_movement(self):
        message = (
            "Chess pieces and how they move:\n\n"
            "1. Pawn (P): Moves forward one square, attacks diagonally.\n"
            "2. Rook (R): Moves horizontally or vertically any number of squares.\n"
            "3. Knight (N): Moves in an 'L' shape (two squares in one direction and then one square perpendicular).\n"
            "4. Bishop (B): Moves diagonally any number of squares.\n"
            "5. Queen (Q): Moves horizontally, vertically, or diagonally any number of squares.\n"
            "6. King (K): Moves one square in any direction.\n"
        )
        messagebox.showinfo("Piece Movements", message)

    def basic_strategies(self):
        message = (
            "Basic chess strategies:\n\n"
            "1. Control the center of the board with your pawns and pieces.\n"
            "2. Develop your knights and bishops early.\n"
            "3. Keep your king safe by castling early.\n"
            "4. Avoid moving the same piece multiple times in the opening.\n"
            "5. Always consider your opponent's threats and think ahead.\n"
        )
        messagebox.showinfo("Basic Strategies", message)

    def create_buttons(self):
        tk.Button(self.buttons_frame, text="Piece Movements", command=self.show_piece_movement, width=20).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(self.buttons_frame, text="Basic Strategies", command=self.basic_strategies, width=20).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.buttons_frame, text="Quit", command=self.root.quit, width=20).grid(row=0, column=2, padx=5, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessTutorialGUI(root)
    root.mainloop()
