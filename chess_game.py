import pygame
import chess_game
import chess.engine

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Chess with Computer')

# Load chess engine
engine = chess_game.engine.SimpleEngine.popen_uci("path_to_your_chess_engine")

# Load images for pieces
pieces = {}
for piece in ['p', 'r', 'n', 'b', 'q', 'k', 'P', 'R', 'N', 'B', 'Q', 'K']:
    pieces[piece] = pygame.image.load(f"images/{piece}.png")

# Function to draw the chessboard
def draw_board(board):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    square_size = width // 8

    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))
            
            piece = board.piece_at(chess_game.square(col, 7 - row))
            if piece:
                screen.blit(pieces[piece.symbol()], pygame.Rect(col * square_size, row * square_size, square_size, square_size))

# Function to get the square under the mouse
def get_square_under_mouse():
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    x, y = [int(v // (width / 8)) for v in mouse_pos]
    return chess_game.square(x, 7 - y)

# Function to handle clicks and move pieces
def handle_clicks(board, selected_square):
    square = get_square_under_mouse()
    if selected_square is None:
        if board.piece_at(square) and board.color_at(square) == chess_game.WHITE:
            return square
    else:
        move = chess_game.Move(selected_square, square)
        if move in board.legal_moves:
            board.push(move)
            return None
        else:
            return selected_square

# Function to play against the computer
def play_against_computer(board, engine):
    if board.turn == chess_game.BLACK:  # Computer's turn
        result = engine.play(board, chess_game.engine.Limit(time=1.0))
        board.push(result.move)

# Main game loop
def main():
    board = chess_game.Board()
    running = True
    selected_square = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and board.turn == chess_game.WHITE:
                selected_square = handle_clicks(board, selected_square)

        if board.turn == chess_game.BLACK:
            play_against_computer(board, engine)

        draw_board(board)
        pygame.display.flip()

    engine.quit()

if __name__ == "__main__":
    main()
