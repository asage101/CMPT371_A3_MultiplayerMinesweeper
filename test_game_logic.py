import random 

def is_valid_cell(row, col, rows, cols):
    #row bounds
    if row < 0 or row >= rows: 
        return False
    #column bounds 
    if col < 0 or col >= cols: 
        return False
    return True

def place_mines(rows, cols, mine_count):
    mines = set()
    while len(mines) < mine_count:
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)
        #duplicatess
        mines.add((r,c))
    return mines

def create_board(rows, cols, mine_count):
    #MT board 
    board = [[0 for _ in range(cols)]for _ in range(rows)]
    #make mines
    mines = place_mines(rows, cols, mine_count)
    #put mines on board
    for r, c in mines: 
        board [r][c] = -1
    #other numbers 
    compute_adj_counts(board)
    return board

def compute_adj_counts(board):
    rows = len(board)
    cols = len(board[0])

    directions = [
        (-1,-1), (-1, 0), (-1, 1),
        (0,-1),          (0,1), 
        (1,-1), (1,0), (1,1)
    ]
    for r in range(rows):
        for c in range(cols):
            #mines don't count
            if board [r][c] == -1:
                continue
            mine_count = 0
            for dr, dc in directions: 
                nr = r + dr
                nc = c + dc

                if is_valid_cell(nr, nc, rows, cols):
                    if board[nr][nc] == -1:
                        mine_count += 1
            board[r][c] = mine_count

def is_mine(board, row, col):
    #is it a mine???
    return board[row][col] == -1

def count_safe_cells(board):
    safe_cells = 0
    for row in board:
        for cell in row:
            if cell != -1:
                safe_cells += 1
    return safe_cells

def create_player_state():
    player_state = { 
        "revealed": set(),
        "alive": True,
        "safe_revealed_count": 0
    }
    return player_state











def test_place_mines():
    rows = 5
    cols = 5
    mine_count = 5

    mines = place_mines(rows, cols, mine_count)

    print("Generated Mines:", mines)

    # Test 1 — correct number of mines
    print("Correct mine count:", len(mines) == mine_count)

    # Test 2 — mines inside board bounds
    valid = True
    for r, c in mines:
        if not is_valid_cell(r, c, rows, cols):
            valid = False

    print("All mines valid positions:", valid)


if __name__ == "__main__":

    print("Testing place_mines()")
    test_place_mines()

def test_create_board():

    rows = 5
    cols = 5
    mines = 5

    board = create_board(rows, cols, mines)

    print("Generated Board:")

    for row in board:
        print(row)

    # Count mines to confirm
    mine_counter = 0
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == -1:
                mine_counter += 1

    print("Correct mine count:", mine_counter == mines)

if __name__ == "__main__":

    print("\nTesting create_board()\n")

    test_create_board()

def test_compute_adj_counts():

    board = [
        [0, 0, -1],
        [0, 0, 0],
        [-1, 0, 0]
    ]

    print("Before:")
    for row in board:
        print(row)

    compute_adj_counts(board)

    print("\nAfter:")
    for row in board:
        print(row)


if __name__ == "__main__":

    print("\nTesting compute_adj_counts()\n")

    test_compute_adj_counts()

def test_is_mine():

    board = [
        [0, -1, 1],
        [1, 2, 1],
        [-1, 1, 0]
    ]

    print("Testing is_mine()")

    print(is_mine(board, 0, 1))  
    print(is_mine(board, 0, 0))  
    print(is_mine(board, 2, 0))  


def test_count_safe_cells():

    board = [
        [0, -1, 1],
        [1, 2, 1],
        [-1, 1, 0]
    ]

    print("Testing count_safe_cells()")

    safe = count_safe_cells(board)

    print("Safe cells:", safe)


if __name__ == "__main__":

    print("\n--- Testing is_mine ---")
    test_is_mine()

    print("\n--- Testing count_safe_cells ---")
    test_count_safe_cells()

def test_create_player_state():

    player = create_player_state()

    print("Player state created:")
    print(player)

    print("Alive:", player["alive"])
    print("Revealed cells:", player["revealed"])
    print("Safe count:", player["safe_revealed_count"])

if __name__ == "__main__":

    print("\n--- Testing create_player_state ---")
    test_create_player_state()