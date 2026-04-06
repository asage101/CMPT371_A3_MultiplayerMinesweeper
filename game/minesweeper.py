#Core minesweeper game logic 
#creation of the board, placing the mines, revealing the cells, and keeping track of the player's progress
import random 

#returns true if the cell is valid (inside the defined rows and columns)
def is_valid_cell(row, col, rows, cols):
    #check the bounds of the input
    if row < 0 or row >= rows: 
        return False
    if col < 0 or col >= cols: 
        return False
    return True


#place the mines randomly on the board 
#ensures that they are all unique positions as well (no more that one mine per cell)
def place_mines(rows, cols, mine_count):
    mines = set()
    while len(mines) < mine_count:
        mine_row = random.randint(0, rows - 1)
        mine_col = random.randint(0, cols - 1)
        mines.add((mine_row, mine_col))
    return mines

#creates the fully hidden game board, mines = -1, all other cells are assigned numbers which share the number of adjacent mines
def create_board(rows, cols, mine_count):
    board = [[0 for _ in range(cols)]for _ in range(rows)]
    mines = place_mines(rows, cols, mine_count)
    for mine_row, mine_col in mines: 
        board [mine_row][mine_col] = -1
    compute_adj_counts(board)
    return board

#fill the non mine cells with the number of mines in the surrounding cells
#requires board to be "built"
def compute_adj_counts(board):
    rows = len(board)
    cols = len(board[0])
    #defines the neighborhood 
    directions = [
        (-1,-1), (-1, 0), (-1, 1),
        (0,-1),          (0,1), 
        (1,-1), (1,0), (1,1)
    ]
    for row in range(rows):
        for col in range(cols):
            #minee already have a value, skip
            if board [row][col] == -1:
                continue
            mine_count = 0
            for drow, dcol in directions: 
                neighbor_row = row + drow
                neighbor_col = col + dcol
                #the neighboorhood is only valid inside the board 
                if is_valid_cell(neighbor_row, neighbor_col, rows, cols):
                    if board[neighbor_row][neighbor_col] == -1:
                        mine_count += 1
            board[row][col] = mine_count

def is_mine(board, row, col):
    #mine check
    return board[row][col] == -1

#calculate the safe cells, used to check if all mines have been cleared
def count_safe_cells(board):
    safe_cells = 0
    for row in board:
        for cell in row:
            if cell != -1:
                safe_cells += 1
    return safe_cells

#creates the player state tracker, number of mines revealed, maintains if the player is alive, and tracks the safe progress 
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
