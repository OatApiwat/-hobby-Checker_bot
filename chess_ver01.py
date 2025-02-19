import chess
import chess.engine
import tkinter as tk
from tkinter import messagebox, simpledialog
import random

class ChessGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Thai Chess")
        self.board = chess.Board()
        self.is_ai_turn = random.choice([True, False])  # Randomly select who starts
        self.ai_difficulty = None
        self.game_started = False  # Track if the game has started

        # Create a canvas to show the board
        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.pack()

        self.label = tk.Label(master, text="")
        self.label.pack()

        self.start_button = tk.Button(master, text="Start Game", command=self.start_game)
        self.start_button.pack()

        self.reset_button = tk.Button(master, text="Reset Game", command=self.reset_game)
        self.reset_button.pack()

        self.confirm_button = tk.Button(master, text="Confirm Move", command=self.confirm_move)
        self.confirm_button.pack()
        self.confirm_button.config(state=tk.DISABLED)  # Disable until the player makes a move

        self.pieces = {}  # Store piece positions
        self.selected_piece = None  # The selected piece
        self.selected_piece_position = None  # The position of the selected piece

        self.draw_board()
        self.load_pieces()
        self.display_player_labels()  # Add labels for AI and Player

    def start_game(self):
        if not self.game_started:  # Ensure the game hasn't started
            self.ai_difficulty = simpledialog.askinteger("AI Difficulty", "Select AI difficulty (1 - Easy, 2 - Medium, 3 - Hard)", minvalue=1, maxvalue=3)
            self.game_started = True  # Mark the game as started
            self.label.config(text="Player's turn (Drag and drop pieces)")
            self.update_turn_display()
            print("Game started. AI difficulty set to:", self.ai_difficulty)

            # Allow AI to make the first move if it starts
            if self.is_ai_turn:
                print("AI starts first.")
                self.make_ai_move()
            else:
                print("Player starts first.")

            self.start_button.config(state=tk.DISABLED)  # Disable start button after starting

    def display_player_labels(self):
        self.ai_label = tk.Label(self.master, text="AI (blue)", fg="blue")
        self.ai_label.pack(side=tk.TOP)  # AI label at the top
        self.player_label = tk.Label(self.master, text="Player (red)", fg="red")
        self.player_label.pack(side=tk.BOTTOM)  # Player label at the bottom

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#eee", "#ccc"]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(col * 50, row * 50, (col + 1) * 50, (row + 1) * 50, fill=color)

    def load_pieces(self):
        piece_mapping = {
            chess.PAWN: '♟', chess.KNIGHT: '♞', chess.BISHOP: '♗', chess.ROOK: '♖',
            chess.QUEEN: '♕', chess.KING: '♔'
        }
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row = chess.square_rank(square)
                col = chess.square_file(square)
                text = piece_mapping[piece.piece_type]
                color = "blue" if piece.color == chess.WHITE else "red"  # Blue for Player, Red for AI
                x = col * 50 + 25
                y = row * 50 + 25
                self.pieces[square] = self.canvas.create_text(x, y, text=text, font=("Arial", 24), fill=color)

        self.canvas.bind("<Button-1>", self.select_piece)  # Click to select a piece
        self.canvas.bind("<B1-Motion>", self.move_piece)  # Drag piece
        self.canvas.bind("<ButtonRelease-1>", self.release_piece)  # Release piece

    def update_turn_display(self):
        if self.is_ai_turn:
            self.label.config(text="AI's turn")
            print("AI's turn.")
        else:
            self.label.config(text="Player's turn (Drag and drop pieces)")
            print("Player's turn.")

    def select_piece(self, event):
        if not self.is_ai_turn and self.game_started:  # Only players can select pieces
            x, y = event.x, event.y
            col, row = x // 50, y // 50
            square = chess.square(col, row)

            if square in self.pieces:  # If there's a piece at that position
                self.selected_piece = self.pieces[square]
                self.selected_piece_position = square
                print(f"Selected piece at square: {square}")

    def move_piece(self, event):
        if self.selected_piece:
            # Move the piece based on mouse position
            self.canvas.coords(self.selected_piece, event.x, event.y)

    def release_piece(self, event):
        if self.selected_piece:
            x, y = event.x, event.y
            col, row = x // 50, y // 50
            target_square = chess.square(col, row)

            if self.selected_piece_position is not None:
                move = chess.Move(self.selected_piece_position, target_square)

                # Check if the move is legal
                if move in self.board.legal_moves:
                    self.board.push(move)
                    print(f"Player moved: {move}")
                    self.update_board()
                    self.is_ai_turn = True  # Switch to AI
                    self.update_turn_display()
                    self.confirm_button.config(state=tk.NORMAL)  # Enable confirmation button

                    if not self.board.is_game_over():
                        print("Waiting for player confirmation for AI's turn.")
                else:
                    messagebox.showerror("Invalid Move", "This move is not legal.")
                    print("Invalid move attempted.")

            self.selected_piece = None
            self.selected_piece_position = None

    def confirm_move(self):
        print("Player confirmed the move.")
        self.confirm_button.config(state=tk.DISABLED)  # Disable until next player move

        if not self.board.is_game_over():
            self.make_ai_move()  # Make AI move after confirmation

    def update_board(self):
        self.canvas.delete("all")
        self.draw_board()
        self.load_pieces()  # Reload pieces

        if self.board.is_game_over():
            self.show_game_over()

    def make_ai_move(self):
        # Start chess engine
        engine = chess.engine.SimpleEngine.popen_uci("D:\\Project\\Checker_bot\\stockfish\\stockfish-windows-x86-64-avx2.exe")  # Change to your engine path
        
        # Set difficulty level
        if self.ai_difficulty == 1:
            time_limit = 1.0
        elif self.ai_difficulty == 2:
            time_limit = 2.0
        else:  # High difficulty
            time_limit = 3.0
        
        result = engine.play(self.board, chess.engine.Limit(time=time_limit))
        self.board.push(result.move)
        print(f"AI moved: {result.move}")
        self.update_board()
        engine.quit()

        if not self.board.is_game_over():
            self.is_ai_turn = False  # Switch to Player
            self.update_turn_display()

    def show_game_over(self):
        winner = "AI" if self.board.result() == "0-1" else "Player"
        messagebox.showinfo("Game Over", f"{winner} wins!")
        print("Game Over. Winner:", winner)
        self.reset_game()

    def reset_game(self):
        self.board.reset()
        self.is_ai_turn = random.choice([True, False])  # Randomly select who starts
        self.label.config(text="")
        self.update_board()
        self.start_button.config(state=tk.NORMAL)  # Enable start button again
        self.confirm_button.config(state=tk.DISABLED)  # Disable confirm button

        self.game_started = False  # Mark the game as not started
        print("Game reset.")

if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
