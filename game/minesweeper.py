import random 

def is_valid_cell(row, col, rows, cols):
    #check the bounds of the input
    if row < 0 or row >= rows: 
        return False
    if col < 0 or col >= cols: 
        return False
    return True


#place the mines randomly on the board
def place_mines(rows, cols, mine_count):
    mines = set()
    while len(mines) < mine_count:
        mine_row = random.randint(0, rows - 1)
        mine_col = random.randint(0, cols - 1)
        mines.add((mine_row, mine_col))
    return mines

#create the board with mines and the adjacent mine numbers
def create_board(rows, cols, mine_count):
    board = [[0 for _ in range(cols)]for _ in range(rows)]
    mines = place_mines(rows, cols, mine_count)
    for mine_row, mine_col in mines: 
        board [mine_row][mine_col] = -1
    compute_adj_counts(board)
    return board

#fill the non mine cells
def compute_adj_counts(board):
    rows = len(board)
    cols = len(board[0])

    directions = [
        (-1,-1), (-1, 0), (-1, 1),
        (0,-1),          (0,1), 
        (1,-1), (1,0), (1,1)
    ]
    for row in range(rows):
        for col in range(cols):
            #mines don't count
            if board [row][col] == -1:
                continue
            mine_count = 0
            for drow, dcol in directions: 
                neighbor_row = row + drow
                neighbor_col = col + dcol

                if is_valid_cell(neighbor_row, neighbor_col, rows, cols):
                    if board[neighbor_row][neighbor_col] == -1:
                        mine_count += 1
            board[row][col] = mine_count

def is_mine(board, row, col):
    #mine check
    return board[row][col] == -1

#calculate the safe cells
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

#reveal one cell
#error: already visible or input invalid 
#mine: mine hit
#safe: safe cell visible
def reveal_cell(board, player_state, row, col):
    rows = len(board)
    cols = len(board[0])

    #check bounds
    if not is_valid_cell(row, col, rows, cols):
        return{
            "status": "error",
            "message": "Invalid move"
        }


    #already flipped
    if (row, col) in player_state["revealed"]:
        return{
            "status":"error",
            "message": "Cell already revealed"
        }

    #mine check
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

#bounds check
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

#check if its already visible
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

#check the mine test
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

'''
if __name__ == "__main__":
    test_reveal_cell_invalid()
    print()

    test_reveal_cell_already_revealed()
    print()

    test_reveal_cell_mine()
    print()

    test_reveal_cell_safe()
'''