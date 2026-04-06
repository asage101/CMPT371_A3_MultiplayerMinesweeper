import socket
import sys
import os 
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import HOST, PORT


#Initial Board
#all values hidden
def create_visible_board(rows,cols):
    return[["." for _ in range(cols)] for _ in range(rows)]

#make the initial board pretty
def print_visible_board(board):
    rows = len(board)
    cols = len(board[0])

    print("  " + " ".join(str(col) for col in range(cols)))

    for row_index in range(rows):
        row_string = " ".join(str(cell) for cell in board[row_index])
        print(f"{row_index} {row_string}")

#create the actual game
def render_game_view(visible_board, your_progress, opponent_progress, last_result_message):
    if last_result_message:
        print(last_result_message)
    print(f"Your progress: {your_progress} safe cells")
    print(f"Opponent progress:{opponent_progress} safe cells")
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
    #print ("client start")

    #creating the TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print("client socket bam")  


    try:
        client_socket.connect((HOST,PORT))
        #print(f"hots{HOST}, PORt {PORT}")
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
        #print(f"Sent: JOIN {username}")

        
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
            #data = client_socket.recv(1024)
            data = line
            if not data:
                print("server disconnected")
                game_over = True
                break
            #message = data.decode().strip()
            message = data.strip()
            if message.startswith("START"):
                parts = message.split()

                rows = int(parts[1])
                cols = int(parts[2])
                mine_count = int(parts[3])

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

                    reveal_message = f"REVEAL {row} {col}\n"
                    client_socket.sendall(reveal_message.encode())
                    #print(f"Sent: REVEAL {row} {col}")

                    move_done = False

                    while not move_done and not game_over:
                        line = client_reader.readline()

                        if not line:
                            print("Server disconnected")
                            game_over = True
                            return

                        response = line.strip()

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

                            #move_done = True
                            #game_over = True

                        elif response.startswith("ERROR"):
                            last_result_message = response
                            render_game_view(
                                visible_board, 
                                your_progress, 
                                opponent_progress, 
                                last_result_message
                            )
                            move_done = True

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
                print(f"Recieved:{message}")

    finally:
        client_socket.close()
        #print("client done")


if __name__ == "__main__":
    start_client()

