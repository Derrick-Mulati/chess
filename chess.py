import pygame
import chess
import chess.engine

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Chess with Computer')

# Load chess engine
engine = chess.engine.SimpleEngine.popen_uci("path_to_your_chess_engine")

# Function to draw the chessboard
def draw_board():
    colors = [pygame.Color("white"), pygame.Color("gray")]
    square_size = width // 8

    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))

# Function to get the square under the mouse
def get_square_under_mouse():
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    x, y = [int(v // (width / 8)) for v in mouse_pos]
    return chess.square(x, 7 - y)

# Function to handle clicks and move pieces
def handle_clicks(board):
    square = get_square_under_mouse()
    move = chess.Move.from_uci(f"{board.peek().uci()[:2]}{chess.square_name(square)}")
    if move in board.legal_moves:
        board.push(move)

# Function to play against the computer
def play_against_computer(board, engine):
    if board.turn == chess.BLACK:  # Computer's turn
        result = engine.play(board, chess.engine.Limit(time=1.0))
        board.push(result.move)

# Main game loop
def main():
    board = chess.Board()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and board.turn == chess.WHITE:
                handle_clicks(board)

        if board.turn == chess.BLACK:
            play_against_computer(board, engine)

        draw_board()
        pygame.display.flip()

    engine.quit()

if __name__ == "__main__":
    main()
