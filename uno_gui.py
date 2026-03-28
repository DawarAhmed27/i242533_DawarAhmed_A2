import random
import tkinter as tk
import time

# ===== CARD CLASS =====
class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = str(value)

    def __repr__(self):
        return f"{self.color} {self.value}"
    
    def matches(self, other_card):
        return self.color == other_card.color or self.value == other_card.value

# ===== DECK GENERATOR =====
def generate_deck():
    colors = ['Red', 'Blue', 'Green', 'Yellow']
    numbers = list(range(10))
    
    deck = []
    for color in colors:
        for num in numbers:
            deck.append(Card(color, num))
        deck.append(Card(color, 'Skip'))
        
    random.shuffle(deck)
    return deck

# ===== VALID MOVES GENERATOR =====
def get_valid_moves(hand, top_card):
    valid_moves = []
    for card in hand:
        if card.matches(top_card):
            valid_moves.append(card)
    return valid_moves

# ===== GAMESTATE CLASS =====
class GameState:
    def __init__(self, ai_cards, opponent1_card_count, opponent2_card_count, top_card, deck):
        self.ai_cards = ai_cards
        self.opponent1_cards = opponent1_card_count
        self.opponent2_cards = opponent2_card_count
        self.top_card = top_card
        self.deck = deck if isinstance(deck, list) else []
        
    def __repr__(self):
        return f"Top: {self.top_card} | AI Cards: {len(self.ai_cards)} | Opp1: {self.opponent1_cards} | Opp2: {self.opponent2_cards} | Deck: {len(self.deck)}"

# ===== EVALUATION FUNCTION =====
def evaluate_state(state, strategy="Defensive"):
    c_ai = len(state.ai_cards)
    c_opp = (state.opponent1_cards + state.opponent2_cards) / 2.0
    s_count = sum(1 for card in state.ai_cards if card.value == 'Skip')
    
    score = 50 - (5 * c_ai) + (2 * c_opp) + (3 * s_count)
    
    if strategy == "Defensive":
        if state.opponent1_cards <= 1 or state.opponent2_cards <= 1:
            score -= 20
        score += (2 * s_count)
    elif strategy == "Offensive":
        if c_ai <= 1:
            score += 20
        score -= (2 * c_ai)
        
    return score

#SimulateMove
def simulate_move(state, move, player_turn):
    new_ai_cards = state.ai_cards.copy()
    new_opponent1_cards = state.opponent1_cards
    new_opponent2_cards = state.opponent2_cards
    new_top_card = state.top_card
    new_deck = state.deck.copy() if isinstance(state.deck, list) else []
    
    if player_turn == 0:
        if move == "Draw":
            if len(new_deck) > 0:
                drawn_card = new_deck.pop(0)
                new_ai_cards.append(drawn_card)
        else:
            for c in new_ai_cards:
                if c.color == move.color and c.value == move.value:
                    new_ai_cards.remove(c)
                    new_top_card = move
                    break
    elif player_turn == 1:
        if move == "Draw":
            if len(new_deck) > 0:
                new_deck.pop(0)
                new_opponent1_cards += 1
        else:
            new_opponent1_cards -= 1
            new_top_card = move
    elif player_turn == 2:
        if move == "Draw":
            if len(new_deck) > 0:
                new_deck.pop(0)
                new_opponent2_cards += 1
        else:
            new_opponent2_cards -= 1
            new_top_card = move
            
    return GameState(new_ai_cards, new_opponent1_cards, new_opponent2_cards, new_top_card, new_deck)

# ===== MINIMAX ALGORITHM =====
def minimax(state, depth, alpha, beta, player_turn):
    if depth == 0 or len(state.ai_cards) == 0 or state.opponent1_cards == 0 or state.opponent2_cards == 0:
        return evaluate_state(state, "Defensive"), None
        
    if player_turn == 0:
        max_eval = float('-inf')
        best_move = None
        
        valid_moves = get_valid_moves(state.ai_cards, state.top_card)
        if not valid_moves:
            valid_moves = ["Draw"]
            
        for move in valid_moves:
            new_state = simulate_move(state, move, player_turn)
            eval_score, _ = minimax(new_state, depth - 1, alpha, beta, 1)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
                
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break 
        return max_eval, best_move
    else:
        min_eval = float('inf')
        possible_moves = [state.top_card, "Draw"]
        
        for move in possible_moves:
            new_state = simulate_move(state, move, player_turn)
            next_turn = 2 if player_turn == 1 else 0
            
            eval_score, _ = minimax(new_state, depth - 1, alpha, beta, next_turn)
            
            if eval_score < min_eval:
                min_eval = eval_score
                
            beta = min(beta, eval_score)
            if beta <= alpha:
                break 
        return min_eval, None

# ===== EXPECTIMAX ALGORITHM =====
def expectimax(state, depth, player_turn):
    if depth == 0 or len(state.ai_cards) == 0 or state.opponent1_cards == 0 or state.opponent2_cards == 0:
        return evaluate_state(state, "Offensive"), None
        
    if player_turn == 0:
        max_eval = float('-inf')
        best_move = None
        
        valid_moves = get_valid_moves(state.ai_cards, state.top_card)
        if not valid_moves:
            valid_moves = ["Draw"]
            
        for move in valid_moves:
            new_state = simulate_move(state, move, player_turn)
            eval_score, _ = expectimax(new_state, depth - 1, 1)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
                
        return max_eval, best_move
    else:
        expected_eval = 0
        possible_moves = [state.top_card, "Draw"]
        
        for move in possible_moves:
            if move == "Draw" and isinstance(state.deck, list) and len(state.deck) > 0:
                deck_len = len(state.deck)
                draw_expected = 0
                for drawn_card in state.deck:
                    probability = 1.0 / deck_len
                    if drawn_card.matches(state.top_card):
                        temp_deck = [c for c in state.deck if c != drawn_card]
                        if player_turn == 1:
                            temp_state = GameState(state.ai_cards, state.opponent1_cards + 1, state.opponent2_cards, drawn_card, temp_deck)
                        else:
                            temp_state = GameState(state.ai_cards, state.opponent1_cards, state.opponent2_cards + 1, drawn_card, temp_deck)
                    else:
                        temp_deck = [c for c in state.deck if c != drawn_card]
                        if player_turn == 1:
                            temp_state = GameState(state.ai_cards, state.opponent1_cards + 1, state.opponent2_cards, state.top_card, temp_deck)
                        else:
                            temp_state = GameState(state.ai_cards, state.opponent1_cards, state.opponent2_cards + 1, state.top_card, temp_deck)
                    next_turn = 2 if player_turn == 1 else 0
                    eval_score, _ = expectimax(temp_state, depth - 1, next_turn)
                    draw_expected += probability * eval_score
                expected_eval += draw_expected
            else:
                new_state = simulate_move(state, move, player_turn)
                next_turn = 2 if player_turn == 1 else 0
                eval_score, _ = expectimax(new_state, depth - 1, next_turn)
                expected_eval += eval_score
        expected_eval = expected_eval / len(possible_moves)
        return expected_eval, None

# ===== COLOR SCHEME =====
COLOR_SCHEME = {
    'Red': '#E74C3C',
    'Blue': '#3498DB',
    'Green': '#2ECC71',
    'Yellow': '#F39C12',
    'bg_dark': '#1a1a2e',
    'bg_light': '#16213e',
    'accent': '#0F3460'
}

def get_card_color(color_name):
    """Convert card color to display color"""
    return COLOR_SCHEME.get(color_name, '#95A5A6')

# ===== TREE PRINTER WITH DEPTH LABELS =====
def print_game_tree(state, depth=3, indent="", player_turn=0):
    # Terminal node: show evaluation score
    if depth == 0:
        score = evaluate_state(state, "Defensive")
        print(indent + "Eval: " + str(score))
        return
    
    # Get valid moves
    moves = get_valid_moves(state.ai_cards, state.top_card)
    if not moves:
        moves = ["Draw"]
    
    # Determine node label by depth
    if depth == 3:
        label = "P1 (Minimax - MAX)"
    elif depth == 2:
        label = "P2 (Opponent)"
    elif depth == 1:
        label = "P3 (MIN)"
    else:
        label = "Terminal"
    
    # Print node label at root
    if indent == "":
        print(label)
    
    # Print all moves
    for i, move in enumerate(moves):
        is_last = (i == len(moves) - 1)
        symbol = "└" if is_last else "├"
        move_str = move if move == "Draw" else str(move)
        print(indent + symbol + "-- " + move_str)
        
        # Simulate and go deeper
        new_state = simulate_move(state, move, 0)
        next_indent = indent + ("  " if is_last else "| ")
        next_depth = depth - 1
        next_player = (player_turn + 1) % 3
        
        # Label next level
        if next_depth > 0:
            if next_depth == 2:
                next_label = "CHANCE" if move == "Draw" else "P2"
            elif next_depth == 1:
                next_label = "CHANCE" if move == "Draw" else "P3"
            else:
                next_label = ""
            
            if next_label:
                print(next_indent + "- " + next_label)
                deeper_indent = next_indent + "  "
            else:
                deeper_indent = next_indent
        else:
            deeper_indent = next_indent
        
        # Recurse
        print_game_tree(new_state, next_depth, deeper_indent, next_player)

# ===== PRINT ALL DECISIONS WITH SCORES =====
def print_decisions_with_scores(state, algorithm="minimax"):
    """Print all possible moves with their expected scores"""
    print("\n" + "─"*70)
    print(f"AI DECISION (All possible decisions considered at depth 1):")
    print("─"*70)
    
    moves = get_valid_moves(state.ai_cards, state.top_card)
    if not moves:
        moves = ["Draw"]
    
    move_scores = []
    
    if algorithm == "minimax":
        for move in moves:
            new_state = simulate_move(state, move, 0)
            score, _ = minimax(new_state, 2, float('-inf'), float('inf'), 1)
            move_scores.append((move, score))
    else:  # expectimax
        for move in moves:
            new_state = simulate_move(state, move, 0)
            score, _ = expectimax(new_state, 2, 1)
            move_scores.append((move, score))
    
    for move, score in sorted(move_scores, key=lambda x: x[1], reverse=True):
        move_str = str(move) if move != "Draw" else "Draw"
        print("Move:", move_str, "| Score:", score)
    
    print("─"*70 + "\n")

#ManualPlayerInput
def get_manual_move_gui(hand, top_card):
    """Display hand with options and get player input for manual mode"""
    print(f"\n{'='*60}")
    print("PLAYER 3 - MANUAL MODE - YOUR TURN")
    print(f"{'='*60}")
    print(f"Top Card: {top_card}")
    print("\nYour Hand:")
    for i, card in enumerate(hand, 1):
        print(f"  {i}. {card}")
    print("  0. Draw")
    choice=input("\nEnter your choice (0 to draw, or card number): ").strip()
    if choice=="0":
        return "Draw"
    try:
        card_idx=int(choice)-1
        if card_idx<0 or card_idx>=len(hand):
            print("Invalid selection!")
            return get_manual_move_gui(hand, top_card)
        chosen_card=hand[card_idx]
        if chosen_card.matches(top_card):
            return chosen_card
        else:
            print("Invalid move!", chosen_card, "doesn't match", top_card)
            return get_manual_move_gui(hand, top_card)
    except ValueError:
        print("Invalid input! Please enter a number.")
        return get_manual_move_gui(hand, top_card)

#ModeSelectionDialog
def get_p3_mode():
    """Simple console dialog to select Player 3 mode"""
    print("\n" + "="*60)
    print("PLAYER 3 MODE SELECTION")
    print("="*60)
    while True:
        print("\nChoose Player 3 mode:")
        print("  (1) Manual (You play as Player 3)")
        print("  (2) Simulation (AI)")
        choice=input("\nEnter your choice (1 or 2): ").strip()
        if choice=="1":
            return "manual"
        elif choice=="2":
            return "simulation"
        else:
            print("Invalid choice! Please enter 1 or 2.")

#TkinterGUIGame
def play_uno_gui(p3_mode="simulation"):
    print("Starting UNO AI Game with GUI")
    print("Starting UNO AI Game with GUI")
    deck = generate_deck()
    
    p1_hand = [deck.pop() for _ in range(5)]
    p2_hand = [deck.pop() for _ in range(5)]
    p3_hand = [deck.pop() for _ in range(5)]
    
    top_card = deck.pop()
    current_player = 0
    game_running = True
    
    # Tkinter Window Setup
    root = tk.Tk()
    root.title("🎮 UNO AI Championship 🎮")
    root.geometry("900x700")
    root.configure(bg=COLOR_SCHEME['bg_dark'])
    root.resizable(False, False)
    
    # ===== HEADER =====
    header_frame = tk.Frame(root, bg=COLOR_SCHEME['accent'], height=80)
    header_frame.pack(fill=tk.X)
    
    title_lbl = tk.Label(header_frame, text="🎮 UNO AI Championship 🎮", 
                        font=("Arial", 24, "bold"), bg=COLOR_SCHEME['accent'], fg="white")
    title_lbl.pack(pady=15)
    
    # ===== TOP CARD AREA (CENTER) =====
    center_frame = tk.Frame(root, bg=COLOR_SCHEME['bg_dark'])
    center_frame.pack(pady=20)
    
    # Current player indicator
    current_player_lbl = tk.Label(center_frame, text="Current Turn: Player 1", 
                                 font=("Arial", 14, "bold"), bg=COLOR_SCHEME['bg_dark'], fg="#2ECC71")
    current_player_lbl.pack(pady=10)
    
    # Top card display
    top_card_container = tk.Frame(center_frame, bg=COLOR_SCHEME['bg_light'], 
                                 borderwidth=3, relief=tk.RIDGE, width=180, height=200)
    top_card_container.pack()
    top_card_container.pack_propagate(False)
    
    top_card_info = tk.Label(top_card_container, text=f"{top_card.value}", 
                            font=("Arial", 60, "bold"), bg=get_card_color(top_card.color), 
                            fg="white")
    top_card_info.pack(expand=True)
    
    top_card_color = tk.Label(top_card_container, text=top_card.color, 
                             font=("Arial", 14, "bold"), bg=get_card_color(top_card.color), 
                             fg="white")
    top_card_color.pack()
    
    # Deck display
    deck_label = tk.Label(center_frame, text=f"📦 Cards Left: {len(deck)}", 
                         font=("Arial", 12), bg=COLOR_SCHEME['bg_dark'], fg="#95A5A6")
    deck_label.pack(pady=10)
    
    # ===== ACTION DISPLAY =====
    action_frame = tk.Frame(root, bg=COLOR_SCHEME['bg_light'], 
                           borderwidth=2, relief=tk.SUNKEN)
    action_frame.pack(fill=tk.X, padx=10, pady=10)
    
    action_lbl = tk.Label(action_frame, text="Game starting...", 
                         font=("Arial", 13, "italic"), bg=COLOR_SCHEME['bg_light'], 
                         fg="#F39C12", wraplength=850)
    action_lbl.pack(pady=10, padx=10)
    
    # ===== PLAYER STATS FRAME =====
    stats_frame = tk.Frame(root, bg=COLOR_SCHEME['bg_dark'])
    stats_frame.pack(fill=tk.X, padx=20, pady=15)
    
    # Player 1 Stats
    p1_frame = tk.Frame(stats_frame, bg=COLOR_SCHEME['bg_light'], 
                       borderwidth=2, relief=tk.RAISED)
    p1_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    p1_name_lbl = tk.Label(p1_frame, text="👥 Player 1", 
                          font=("Arial", 12, "bold"), bg=COLOR_SCHEME['bg_light'], 
                          fg="#E74C3C")
    p1_name_lbl.pack(pady=5)
    
    p1_strategy = tk.Label(p1_frame, text="[Minimax - Defensive]", 
                          font=("Arial", 10), bg=COLOR_SCHEME['bg_light'], 
                          fg="#95A5A6")
    p1_strategy.pack()
    
    p1_cards_lbl = tk.Label(p1_frame, text="🎴 Cards: 5", 
                           font=("Arial", 14, "bold"), bg=COLOR_SCHEME['bg_light'], 
                           fg="white")
    p1_cards_lbl.pack(pady=10)
    
    # Player 2 Stats
    p2_frame = tk.Frame(stats_frame, bg=COLOR_SCHEME['bg_light'], 
                       borderwidth=2, relief=tk.RAISED)
    p2_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    p2_name_lbl = tk.Label(p2_frame, text="👥 Player 2", 
                          font=("Arial", 12, "bold"), bg=COLOR_SCHEME['bg_light'], 
                          fg="#3498DB")
    p2_name_lbl.pack(pady=5)
    
    p2_strategy = tk.Label(p2_frame, text="[Expectimax - Offensive]", 
                          font=("Arial", 10), bg=COLOR_SCHEME['bg_light'], 
                          fg="#95A5A6")
    p2_strategy.pack()
    
    p2_cards_lbl = tk.Label(p2_frame, text="🎴 Cards: 5", 
                           font=("Arial", 14, "bold"), bg=COLOR_SCHEME['bg_light'], 
                           fg="white")
    p2_cards_lbl.pack(pady=10)
    
    # Player 3 Stats
    p3_frame = tk.Frame(stats_frame, bg=COLOR_SCHEME['bg_light'], 
                       borderwidth=2, relief=tk.RAISED)
    p3_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    p3_name_lbl = tk.Label(p3_frame, text="👥 Player 3", 
                          font=("Arial", 12, "bold"), bg=COLOR_SCHEME['bg_light'], 
                          fg="#2ECC71")
    p3_name_lbl.pack(pady=5)
    
    p3_mode_text = "[Manual - You Play]" if p3_mode == "manual" else "[Minimax - AI]"
    p3_strategy = tk.Label(p3_frame, text=p3_mode_text, 
                          font=("Arial", 10), bg=COLOR_SCHEME['bg_light'], 
                          fg="#95A5A6")
    p3_strategy.pack()
    
    p3_cards_lbl = tk.Label(p3_frame, text="🎴 Cards: 5", 
                           font=("Arial", 14, "bold"), bg=COLOR_SCHEME['bg_light'], 
                           fg="white")
    p3_cards_lbl.pack(pady=10)
    
    def update_gui(turn_text, action_text, player_num=None):
        nonlocal top_card, current_player
        
        # Update current player
        player_names = ["Player 1", "Player 2", "Player 3"]
        if player_num is not None:
            current_player_lbl.config(text=f"Current Turn: {player_names[player_num]}")
        
        # Update top card
        top_card_info.config(text=f"{top_card.value}", bg=get_card_color(top_card.color))
        top_card_color.config(bg=get_card_color(top_card.color))
        deck_label.config(text=f"📦 Cards Left: {len(deck)}")
        
        # Update player cards
        p1_cards_lbl.config(text=f"🎴 Cards: {len(p1_hand)}")
        p2_cards_lbl.config(text=f"🎴 Cards: {len(p2_hand)}")
        p3_cards_lbl.config(text=f"🎴 Cards: {len(p3_hand)}")
        
        # Update action
        action_lbl.config(text=f"➤ {action_text}")
        
        root.update()
        time.sleep(1.5)
    
    def game_loop():
        nonlocal current_player, top_card, game_running
        
        while game_running:
            # Check win conditions
            if len(p1_hand) == 0:
                update_gui("Game Over!", "🎉 Player 1 Wins! 🎉", 0)
                print("Player 1 Wins")
                game_running = False
                break
            elif len(p2_hand) == 0:
                update_gui("Game Over!", "🎉 Player 2 Wins! 🎉", 1)
                print("Player 2 Wins")
                game_running = False
                break
            elif len(p3_hand) == 0:
                update_gui("Game Over!", "🎉 Player 3 Wins! 🎉", 2)
                print("Player 3 Wins")
                game_running = False
                break
            if len(deck) == 0:
                update_gui("Game Over!", "Draw Deck Empty - Draw!", None)
                print("Draw Deck Empty")
                game_running = False
                break
                
            # Player 1 Turn
            if current_player == 0:
                state = GameState(p1_hand, len(p2_hand), len(p3_hand), top_card, deck)
                print("\n" + "="*70)
                print("🎮 PLAYER 1 (Minimax - Defensive AI) TURN")
                print("="*70)
                print(f"Top Card: {top_card}")
                print(f"P1 Hand: {p1_hand}")
                print("\n📊 Game Tree (Depth 2):")
                print("┌─ Exploring possible moves...")
                print_game_tree(state, 2)
                print("└─ Tree exploration complete.\n")
                
                # Print all decisions with scores
                print_decisions_with_scores(state, "minimax")
                
                score, move = minimax(state, 3, float('-inf'), float('inf'), 0)
                print(f"✓ BEST MOVE SELECTED: {move} (Minimax Score: {score:.2f})\n")
                
                if move == "Draw" or move is None:
                    if len(deck) > 0:
                        p1_hand.append(deck.pop())
                    update_gui("P1 Turn", "P1 draws a card from deck 🔄", 0)
                    current_player = 1
                else:
                    for c in p1_hand:
                        if c.color == move.color and c.value == move.value:
                            p1_hand.remove(c)
                            break
                    top_card = move
                    if top_card.value == 'Skip':
                        update_gui("P1 Turn", f"P1 plays {move} - P2 is skipped! ⏭️", 0)
                        current_player = 2
                    else:
                        update_gui("P1 Turn", f"P1 plays {move} ✓", 0)
                        current_player = 1
                        
            # Player 2 Turn
            elif current_player == 1:
                state = GameState(p2_hand, len(p3_hand), len(p1_hand), top_card, deck)
                print("\n" + "="*70)
                print("🎮 PLAYER 2 (Expectimax - Offensive AI) TURN")
                print("="*70)
                print(f"Top Card: {top_card}")
                print(f"P2 Hand: {p2_hand}")
                print("\n📊 Game Tree (Depth 2):")
                print("┌─ Exploring possible moves...")
                print_game_tree(state, 2)
                print("└─ Tree exploration complete.\n")
                
                # Print all decisions with scores
                print_decisions_with_scores(state, "expectimax")
                
                score, move = expectimax(state, 3, 0)
                print(f"✓ BEST MOVE SELECTED: {move} (Expectimax Score: {score:.2f})\n")
                
                if move == "Draw" or move is None:
                    if len(deck) > 0:
                        p2_hand.append(deck.pop())
                    update_gui("P2 Turn", "P2 draws a card from deck 🔄", 1)
                    current_player = 2
                else:
                    for c in p2_hand:
                        if c.color == move.color and c.value == move.value:
                            p2_hand.remove(c)
                            break
                    top_card = move
                    if top_card.value == 'Skip':
                        update_gui("P2 Turn", f"P2 plays {move} - P3 is skipped! ⏭️", 1)
                        current_player = 0
                    else:
                        update_gui("P2 Turn", f"P2 plays {move} ✓", 1)
                        current_player = 2
                        
            # Player 3 Turn
            elif current_player == 2:
                if p3_mode == "manual":
                    move=get_manual_move_gui(p3_hand, top_card)
                    if move == "Draw":
                        print("You drew a card")
                        if len(deck) > 0:
                            p3_hand.append(deck.pop())
                        update_gui("P3 Turn", "You drew a card from deck 🔄", 2)
                        current_player = 0
                    else:
                        print(f"You played: {move}")
                        for c in p3_hand:
                            if c.color == move.color and c.value == move.value:
                                p3_hand.remove(c)
                                break
                        top_card = move
                        if top_card.value == 'Skip':
                            update_gui("P3 Turn", f"You played {move} - P1 is skipped! ⏭️", 2)
                            current_player = 1
                        else:
                            update_gui("P3 Turn", f"You played {move} ✓", 2)
                            current_player = 0
                else:
                    state = GameState(p3_hand, len(p1_hand), len(p2_hand), top_card, deck)
                    print("\n" + "="*70)
                    print("🎮 PLAYER 3 (Minimax - Adaptive AI) TURN")
                    print("="*70)
                    print(f"Top Card: {top_card}")
                    print(f"P3 Hand: {p3_hand}")
                    print("\n📊 Game Tree (Depth 2):")
                    print("┌─ Exploring possible moves...")
                    print_game_tree(state, 2)
                    print("└─ Tree exploration complete.\n")
                    print_decisions_with_scores(state, "minimax")
                    score, move = minimax(state, 3, float('-inf'), float('inf'), 0)
                    print(f"✓ BEST MOVE SELECTED: {move} (Minimax Score: {score:.2f})\n")
                    if move == "Draw" or move is None:
                        if len(deck) > 0:
                            p3_hand.append(deck.pop())
                        update_gui("P3 Turn", "P3 draws a card from deck 🔄", 2)
                        current_player = 0
                    else:
                        for c in p3_hand:
                            if c.color == move.color and c.value == move.value:
                                p3_hand.remove(c)
                                break
                        top_card = move
                        if top_card.value == 'Skip':
                            update_gui("P3 Turn", f"P3 plays {move} - P1 is skipped! ⏭️", 2)
                            current_player = 1
                        else:
                            update_gui("P3 Turn", f"P3 plays {move} ✓", 2)
                            current_player = 0
        
        root.after(2000, root.destroy)
    
    root.after(500, game_loop)
    root.mainloop()

if __name__ == "__main__":
    mode=get_p3_mode()
    play_uno_gui(p3_mode=mode)
