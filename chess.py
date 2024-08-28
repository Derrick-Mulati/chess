import chess
import chess.svg

def print_board(board):
    print(board)

def play_chess():
    board = chess.Board()

    while not board.is_game_over():
        print_board(board)
        print("\nCurrent Turn: White" if board.turn else "Current Turn: Black")
        
        try:
            move = input("Enter your move in UCI format (e.g., e2e4): ").strip()
            board.push_uci(move)
        except ValueError:
            print("Invalid move format. Please try again.")
        except Exception as e:
            print(f"Error: {e}")

        print("\n")

    result = "1-0" if board.result() == "1-0" else "0-1" if board.result() == "0-1" else "1/2-1/2"
    print(f"Game Over! Result: {result}")

if __name__ == "__main__":
    play_chess()
