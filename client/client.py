#This file implements the terminal client 
#handles connections to the server, sends player names, and shares responses from the server
import socket
import sys
import os 
#added to allow imports from config.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import HOST, PORT


#Initial Board
#all values hidden
def create_visible_board(rows, cols):
    return[["." for _ in range(cols)] for _ in range(rows)]

#make the initial board pretty
def print_visible_board(board):
    rows = len(board)
    cols = len(board[0])

    print("  " + " ".join(str(col) for col in range(cols)))

    for row_index in range(rows):
        row_string = " ".join(str(cell) for cell in board[row_index])
        print(f"{row_index} {row_string}")

#Displays the client side view of the game (and progress and board state)
def render_game_view(visible_board, your_progress, opponent_progress, last_result_message):
    if last_result_message:
        print(last_result_message)
    print(f"Your progress: {your_progress} safe cells")
    print(f"Opponent progress: {opponent_progress} safe cells")
    print()

    if visible_board is not None:
        print_visible_board(visible_board)
    
    print()
    print("Enter move as: row   col  ")

#read input
def prompt_for_move():
    move_text = input("> ").strip()
    parts = move_text.split()

    if len(parts) != 2:
        return None, None
    return parts[0], parts[1]

#respond to invalid moves 
def get_valid_move():
    while True:
        row_text, col_text = prompt_for_move()

        if row_text is None or col_text is None:
            print("Invalid input. Enter move as: row   col  ")
            continue
        try:
            row = int(row_text)
            col = int(col_text)
            return row, col 
        except ValueError:
            print("Invalid input. Enter integers like: 3 5 ")



#start the client, connect it to the server 
def start_client():


    #creating the TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



    try:
        client_socket.connect((HOST,PORT))
        client_reader = client_socket.makefile("r")
        #player gives username
        while True:
            username = input("Enter username: ").strip()
            if username != "":
                break
            print("Username is required. please enter a username")

        #JOIN
        join_message = f"JOIN {username}\n"
        client_socket.sendall(join_message.encode())


        #used to display the board and track progress
        visible_board = None
        game_started = False
        game_over = False
        waiting_for_move = False

        your_progress = 0
        opponent_progress = 0
        last_result_message = ""

        #communicate with the server
        while not game_over:
            line = client_reader.readline()

            data = line
            if not data:
                print("server disconnected")
                game_over = True
                break

            message = data.strip()
            #START means that both players are connected and match can start
            if message.startswith("START"):
                parts = message.split()

                rows = int(parts[1])
                cols = int(parts[2])
                mine_count = int(parts[3])
                #the client only stores what this player has revelaed, not the hidden layout
                visible_board = create_visible_board(rows,cols)
                game_started = True
                waiting_for_move = False
                last_result_message = f"Game started! Board size {rows} x {cols}. Mines: {mine_count}"


                render_game_view(
                    visible_board, 
                    your_progress, 
                    opponent_progress, 
                    last_result_message
                )
                while not game_over:
                    row, col = get_valid_move()
                    #send the player's move to the server to be checked for validity
                    reveal_message = f"REVEAL {row} {col}\n"
                    client_socket.sendall(reveal_message.encode())

                    move_done = False
                    #after sending a move keep the server response unil the move has been processed or game ends
                    while not move_done and not game_over:
                        line = client_reader.readline()

                        if not line:
                            print("Server disconnected")
                            game_over = True
                            return

                        response = line.strip()
                        #The server confirms this move is safe--> update board 
                        if response.startswith("RESULT SAFE"):
                            parts = response.split()

                            result_row = int(parts[2])
                            result_col = int(parts[3])
                            value = parts[4]

                            if visible_board is None:
                                print("error: there was no visible board created")
                                return

                            visible_board[result_row][result_col] = value
                            last_result_message = f"Safe reveal at ({result_row}, {result_col}): {value} adjacent mines"

                            render_game_view(
                                visible_board, 
                                your_progress, 
                                opponent_progress, 
                                last_result_message
                            )


                            move_done = True
                        #server says mine was hit --> mark as hit on th visible board
                        elif response.startswith("RESULT MINE"):
                            parts = response.split()

                            result_row = int(parts[2])
                            result_col = int(parts[3])

                            if visible_board is None:
                                print("error: there is no visible board")
                                return

                            visible_board[result_row][result_col] = "*"
                            last_result_message = f"Mine hit at ({result_row}, {result_col})"

                            render_game_view(
                                visible_board, 
                                your_progress, 
                                opponent_progress, 
                                last_result_message
                            )



                            
                        elif response.startswith("ERROR"):
                            last_result_message = response
                            render_game_view(
                                visible_board, 
                                your_progress, 
                                opponent_progress, 
                                last_result_message
                            )
                            move_done = True
                        #updates are sent seperately therefore progress you and progress opponent, to track them independently 
                        elif response.startswith("PROGRESS YOU"):
                            parts = response.split()
                            #count = parts[2]
                            your_progress = int(parts[2])
                            
                            render_game_view(
                                visible_board, 
                                your_progress, 
                                opponent_progress, 
                                last_result_message
                            )

                        elif response.startswith("PROGRESS OPPONENT"):
                            parts = response.split()
                            #count = parts[2]
                            opponent_progress = int(parts[2])

                            render_game_view(
                                visible_board, 
                                your_progress, 
                                opponent_progress, 
                                last_result_message
                            )
                        #status updates from the server (win, loss, disconnected)
                        elif response.startswith("MESSAGE "):
                            text = response[len("MESSAGE "):]
                            last_result_message = text
                            render_game_view(
                                visible_board,
                                your_progress,
                                opponent_progress,
                                last_result_message
                            )


                        elif response == "OPPONENT_DISCONNECTED":
                            print("Opponent disconnected. You win by default")
                            game_over = True
                        elif response == "WIN":
                            print("You won!")
                            game_over = True

                        elif response == "LOSE":
                            print("You lost!")
                            game_over = True

                        elif response == "TIE":
                            print("Game ended in a tie.")
                            game_over = True

                        else:
                            print(f"Received: {response}")

                    if game_over:
                        break
                        
                break
            else:
                #deals with pre game messages like WAITING
                print(f"Recieved: {message}")

    finally:
        client_socket.close()
        #print("client done")


if __name__ == "__main__":
    start_client()

