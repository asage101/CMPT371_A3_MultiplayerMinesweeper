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

def reveal_cell(board, player_state, row, col):
    rows = len(board)
    cols = len(board[0])

    #check bounds
    if not is_valid_cell(row, col, rows, cols):
        return{
            "status": "error",
            "message": "Invalid Move"
        }


    #already flipped
    if (row, col) in player_state["revealed"]:
        return{
            "status":"error",
            "message": "Cell already revealed"
        }

    #is it a mine????
    if board[row][col] == -1:
        player_state["revealed"].add((row,col))
        player_state["alive"] = False

        return {
            "status": "mine", 
            "row": row, 
            "col": col
        }

    #if its safe
    player_state["revealed"].add((row,col))
    player_state["safe_revealed_count"] += 1
    cell_value = board[row][col]

    return{
        "status": "safe", 
        "row": row, 
        "col": col, 
        "value": cell_value
    }

def test_reveal_cell_invalid():
    board = [
        [0, 1, -1],
        [1, 2, 1],
        [0, 1, 0]
    ]

    player_state = create_player_state()

    result = reveal_cell(board, player_state, -1, 0)

    print("Invalid move test:")
    print(result)

def test_reveal_cell_already_revealed():
    board = [
        [0, 1, -1],
        [1, 2, 1],
        [0, 1, 0]
    ]

    player_state = create_player_state()
    player_state["revealed"].add((1, 1))

    result = reveal_cell(board, player_state, 1, 1)

    print("Already revealed test:")
    print(result)

def test_reveal_cell_mine():
    board = [
        [0, 1, -1],
        [1, 2, 1],
        [0, 1, 0]
    ]

    player_state = create_player_state()

    result = reveal_cell(board, player_state, 0, 2)

    print("Mine reveal test:")
    print(result)
    print("Player alive:", player_state["alive"])
    print("Revealed cells:", player_state["revealed"])

def test_reveal_cell_safe():
    board = [
        [0, 1, -1],
        [1, 2, 1],
        [0, 1, 0]
    ]

    player_state = create_player_state()

    result = reveal_cell(board, player_state, 1, 1)

    print("Safe reveal test:")
    print(result)
    print("Safe revealed count:", player_state["safe_revealed_count"])
    print("Revealed cells:", player_state["revealed"])


if __name__ == "__main__":
    test_reveal_cell_invalid()
    print()

    test_reveal_cell_already_revealed()
    print()

    test_reveal_cell_mine()
    print()

    test_reveal_cell_safe()