import pygame
import chess
import threading
import time
from operator import itemgetter 

# --- AI CLASS (UNCHANGED) ---
# ... (All previous code for ExplainableChessAI remains the same) ...

class ExplainableChessAI:
    def __init__(self, depth=2):
        self.depth = depth
        # Tunable weights (The "Knowledge")
        self.weights = {
            'pawn': 100, 'knight': 320, 'bishop': 330, 'rook': 500,
            'queen': 900, 'king': 20000, 'mobility': 10, 'center_control': 20
        }
        self.learning_rate = 0.5
        self.last_explanation = ["AI Initialized.", "Ready to play."]

    # Minimax, evaluate_board, get_best_move, and learn methods are the same.
    # --- Minimax and Evaluation (omitted for brevity, unchanged from last version) ---
    def evaluate_board(self, board):
        if board.is_checkmate():
            return -99999 if board.turn else 99999
        if board.is_stalemate() or board.is_insufficient_material(): return 0

        score = 0
        piece_map = board.piece_map()
        for piece in piece_map.values():
            val = self.weights.get(chess.piece_name(piece.piece_type), 0)
            score += val if piece.color == chess.WHITE else -val

        for sq in [chess.E4, chess.D4, chess.E5, chess.D5]:
            p = board.piece_at(sq)
            if p:
                score += self.weights['center_control'] if p.color == chess.WHITE else -self.weights['center_control']

        return score

    def minimax(self, board, depth, alpha, beta, maximizing):
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        moves = sorted(board.legal_moves, key=lambda m: board.is_capture(m), reverse=True)
        
        if maximizing:
            max_eval = -float('inf')
            for move in moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha: break
            return min_eval
    
    def get_best_move(self, board):
        all_move_evals = []
        for move in board.legal_moves:
            board.push(move)
            val = self.minimax(board, self.depth - 1, -float('inf'), float('inf'), not board.turn)
            board.pop()
            all_move_evals.append((move, val))

        if board.turn == chess.WHITE:
            all_move_evals.sort(key=itemgetter(1), reverse=True)
        else:
            all_move_evals.sort(key=itemgetter(1))

        best_move = all_move_evals[0][0] if all_move_evals else None
        top_candidates = all_move_evals[:3]
        
        if best_move:
            self.last_explanation = [f"AI Move: {board.san(best_move)} (Score: {top_candidates[0][1]:.2f})"]
            for i, (move, score) in enumerate(top_candidates[1:]):
                 self.last_explanation.append(f"#{i+2} Cand.: {board.san(move)} (Score: {score:.2f})")
            
        return best_move, top_candidates

    def learn(self, winner_color):
        msg = "Game Over. "
        if winner_color == chess.WHITE:
            msg += "AI Lost."
            self.weights['center_control'] += 5
            self.weights['mobility'] += 2
            self.last_explanation = [msg, "Learning: Increased valuation", "of center control & mobility."]
        elif winner_color == chess.BLACK:
            msg += "AI Won."
            self.last_explanation = [msg, "Strategy successful.", "Reinforcing current approach."]
        else:
            self.last_explanation = ["Draw.", "No weights adjusted."]


# --- GUI CONSTANTS ---
WIDTH, HEIGHT = 900, 600
BOARD_SIZE = 600
SQ_SIZE = BOARD_SIZE // 8
FPS = 60

# Modern Aesthetic Colors
DARK_WOOD = (181, 136, 99) 
LIGHT_WOOD = (240, 217, 181)
PANEL_BG = (25, 25, 25)
TEXT_COLOR = (240, 240, 240)
HIGHLIGHT_SELECT = (255, 255, 0, 150)

# Button Colors
BUTTON_COLOR = (80, 80, 80)
BUTTON_HOVER_COLOR = (120, 120, 120)
BUTTON_TEXT_COLOR = (255, 255, 255)

# Candidate Visualization Colors
CANDIDATE_1_COLOR = (255, 165, 0)
CANDIDATE_2_COLOR = (255, 0, 0)
BEST_MOVE_COLOR = (0, 255, 0)


class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("AI Chess Dojo v2: Visual Thinking")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('segoe ui symbol', 50) 
        self.ui_font = pygame.font.SysFont('arial', 20)
        
        self.board = chess.Board()
        self.ai = ExplainableChessAI(depth=3)
        self.selected_square = None
        
        self.training_mode = False
        self.ai_thinking = False
        self.game_over = False
        self.ai_candidates = []
        
        # Define the restart button area
        self.restart_button_rect = pygame.Rect(BOARD_SIZE + 40, HEIGHT - 80, 220, 50)
        self.restart_button_text = self.ui_font.render("RESTART GAME", True, BUTTON_TEXT_COLOR)
        
    def get_pos(self, square):
        col = chess.square_file(square)
        row = 7 - chess.square_rank(square)
        return col * SQ_SIZE, row * SQ_SIZE

    def draw_board(self):
        for r in range(8):
            for c in range(8):
                color = LIGHT_WOOD if (r + c) % 2 == 0 else DARK_WOOD
                rect = (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                
                sq_index = chess.square(c, 7-r)
                if self.selected_square == sq_index:
                    pygame.draw.rect(self.screen, HIGHLIGHT_SELECT, rect, 4)

                if self.selected_square:
                    move = chess.Move(self.selected_square, sq_index)
                    if move in self.board.legal_moves:
                        center = (c * SQ_SIZE + SQ_SIZE//2, r * SQ_SIZE + SQ_SIZE//2)
                        pygame.draw.circle(self.screen, (0, 200, 0), center, 10)

    def draw_candidates(self):
        if not self.ai_candidates: return
        
        # Best Move (Green Arrow)
        best_move = self.ai_candidates[0][0]
        start_pos = self.get_pos(best_move.from_square)
        end_pos = self.get_pos(best_move.to_square)
        
        start_center = (start_pos[0] + SQ_SIZE//2, start_pos[1] + SQ_SIZE//2)
        end_center = (end_pos[0] + SQ_SIZE//2, end_pos[1] + SQ_SIZE//2)
        pygame.draw.line(self.screen, BEST_MOVE_COLOR, start_center, end_center, 5)
        pygame.draw.circle(self.screen, BEST_MOVE_COLOR, end_center, 12)

        # Other Candidates (Yellow/Red Circles)
        for i, (move, score) in enumerate(self.ai_candidates[1:]):
            to_sq = move.to_square
            center = self.get_pos(to_sq)
            center = (center[0] + SQ_SIZE//2, center[1] + SQ_SIZE//2)
            
            color = CANDIDATE_1_COLOR if i == 0 else CANDIDATE_2_COLOR
            pygame.draw.circle(self.screen, color, center, 8)
            pygame.draw.circle(self.screen, (0, 0, 0), center, 5)

    def draw_pieces(self):
        pieces = {'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
                  'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'}
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                symbol = pieces[piece.symbol()]
                text_color = (0, 0, 0) if piece.color == chess.BLACK else (255, 255, 255)

                text = self.font.render(symbol, True, text_color)
                
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)
                rect = text.get_rect(center=(col * SQ_SIZE + SQ_SIZE//2, row * SQ_SIZE + SQ_SIZE//2))
                self.screen.blit(text, rect)

    def draw_ui(self):
        # Sidebar background
        pygame.draw.rect(self.screen, PANEL_BG, (BOARD_SIZE, 0, WIDTH - BOARD_SIZE, HEIGHT))
        
        # Header and Mode Indicator (unchanged)
        title = self.ui_font.render("AI Thinking & Learning Log", True, (255, 215, 0))
        self.screen.blit(title, (BOARD_SIZE + 20, 20))
        
        mode_text = "MODE: TRAINING (AI vs AI)" if self.training_mode else "MODE: HUMAN vs AI"
        mode_color = (255, 100, 100) if self.training_mode else (100, 255, 100)
        mode_surf = self.ui_font.render(mode_text, True, mode_color)
        self.screen.blit(mode_surf, (BOARD_SIZE + 20, 50))
        
        instr = self.ui_font.render("Press 'T' to toggle Train Mode", True, (150, 150, 150))
        self.screen.blit(instr, (BOARD_SIZE + 20, 80))

        pygame.draw.line(self.screen, (50, 50, 50), (BOARD_SIZE + 10, 110), (WIDTH - 10, 110), 2)

        # AI Logs (Explanation)
        y_offset = 130
        for line in self.ai.last_explanation:
            text = self.ui_font.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (BOARD_SIZE + 20, y_offset))
            y_offset += 30
            
        # Stats (Weights)
        if self.training_mode:
            stats = [
                f"--- AI Current Values ---",
                f"Pawn: {self.ai.weights['pawn']}",
                f"Center Control: {self.ai.weights['center_control']:.1f}",
                f"Mobility: {self.ai.weights['mobility']:.1f}"
            ]
            y_stat = 400
            for s in stats:
                t = self.ui_font.render(s, True, (100, 200, 255))
                self.screen.blit(t, (BOARD_SIZE + 20, y_stat))
                y_stat += 30
                
        # Draw Restart Button
        is_hover = self.restart_button_rect.collidepoint(pygame.mouse.get_pos())
        color = BUTTON_HOVER_COLOR if is_hover else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, self.restart_button_rect, border_radius=5)
        
        text_rect = self.restart_button_text.get_rect(center=self.restart_button_rect.center)
        self.screen.blit(self.restart_button_text, text_rect)

    def handle_restart_button(self, click_pos):
        """Checks if the click was on the restart button and resets the game."""
        if self.restart_button_rect.collidepoint(click_pos):
            self.board.reset()
            self.game_over = False
            self.selected_square = None
            self.ai_candidates = []
            self.ai.last_explanation = ["Game manually restarted.", "AI knowledge preserved."]
            return True
        return False

    def run_ai_move(self):
        self.ai_thinking = True
        best_move, candidates = self.ai.get_best_move(self.board)
        self.ai_candidates = candidates
        
        if best_move:
            self.board.push(best_move)
        
        self.ai_thinking = False

    def handle_game_over(self):
        outcome = self.board.outcome()
        winner = outcome.winner
        self.ai.learn(winner)
        self.ai_candidates = []
        
        if self.training_mode:
            pygame.display.flip()
            time.sleep(0.1) 
            self.board.reset()
        else:
            self.game_over = True

    def main_loop(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                    self.training_mode = not self.training_mode
                    self.ai.last_explanation = ["Switched Mode."]

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.handle_restart_button(event.pos):
                        # Button clicked, game reset. Skip rest of loop.
                        continue
                        
                    if not self.game_over and not self.training_mode:
                        if self.board.turn == chess.WHITE: # Human Turn
                            x, y = event.pos
                            if x < BOARD_SIZE:
                                col = x // SQ_SIZE
                                row = 7 - (y // SQ_SIZE)
                                clicked_sq = chess.square(col, row)
                                
                                if self.selected_square is not None:
                                    move = chess.Move(self.selected_square, clicked_sq)
                                    if self.board.piece_at(self.selected_square) and self.board.piece_at(self.selected_square).piece_type == chess.PAWN and chess.square_rank(clicked_sq) == 7:
                                        move = chess.Move(self.selected_square, clicked_sq, promotion=chess.QUEEN)

                                    if move in self.board.legal_moves:
                                        self.board.push(move)
                                        self.selected_square = None
                                        self.ai_candidates = []
                                    else:
                                        if self.board.piece_at(clicked_sq) and self.board.piece_at(clicked_sq).color == chess.WHITE:
                                            self.selected_square = clicked_sq
                                        else:
                                             self.selected_square = None
                                else:
                                    if self.board.piece_at(clicked_sq) and self.board.piece_at(clicked_sq).color == chess.WHITE:
                                        self.selected_square = clicked_sq

            # Game Logic
            if not self.game_over:
                if self.board.is_game_over():
                    self.handle_game_over()
                
                elif self.training_mode or (self.board.turn == chess.BLACK and not self.ai_thinking):
                    pygame.display.flip()
                    if not self.training_mode:
                        time.sleep(0.1) 
                    self.run_ai_move()

            # Drawing
            self.screen.fill(PANEL_BG)
            self.draw_board()
            self.draw_candidates()
            self.draw_pieces()
            self.draw_ui()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    gui = ChessGUI()
    gui.main_loop()