import socket
import sys
import os
import threading

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from game.minesweeper import create_board, count_safe_cells, create_player_state, reveal_cell
from config import HOST, PORT, ROWS, COLS, MINE_COUNT, JOIN_TIMEOUT


def recv_line(client_socket):
    try:
        #recieving message from client
        data = client_socket.recv(1024)
        if not data:
            return ""
        return data.decode().strip()
    except (ConnectionAbortedError, ConnectionResetError, OSError):
        return ""


def send_line(client_socket, message):
    #send one line to client
    try:
        if not message.endswith("\n"):
            message += "\n"

        client_socket.sendall(message.encode())
    except(ConnectionAbortedError, ConnectionResetError, OSError) as e:
        print(f"Send failed: {e}")


def finalize_match(match_state, winner, final_reason):
    if match_state["game_over"]:
        return
    match_state["game_over"] = True
    match_state["winner"] = winner
    match_state["final_reason"] = final_reason

#if one player disconnects 
def handle_disconnect(match_state, match_lock, disconnected_player_id):
    with match_lock:
        if match_state["game_over"]:
            return
        
        if disconnected_player_id == 1:
            opponent_id = 2
        else:
            opponent_id = 1
        disconnected_player = match_state["players"][disconnected_player_id]
        opponent = match_state["players"][opponent_id]

        finalize_match(match_state, opponent_id, "disconnect")

        send_line(opponent["socket"], "MESSAGE Opponent disconnected.")
        send_line(opponent["socket"], "OPPONENT_DISCONNECTED")

        print(f"{disconnected_player['username']} disconnected. {opponent['username']} wins by default")
        
#dealing with messageing for each player 
#each player has a handler thread to allow independent play. 
#lock is used to prevent any interference between the 2
def handle_client(player_id, match_state, match_lock):
    player = match_state["players"][player_id]
    if player_id == 1:
        opponent_id = 2
    else:
        opponent_id = 1
    
    opponent = match_state["players"][opponent_id]

    player_socket = player["socket"]
    username = player["username"]

    recv_buffer = ""
    print(f"Handler started for {username}")
    try:
        while True:
            while "\n" not in recv_buffer:
                try:
                    chunk = player_socket.recv(1024)
                except (ConnectionAbortedError, ConnectionResetError, OSError):
                    chunk = b""
                if not chunk:
                    print(f"{username} disconnected")
                    handle_disconnect(match_state, match_lock, player_id)
                    return
                recv_buffer += chunk.decode()
            line, recv_buffer = recv_buffer.split("\n",1)
            line = line.strip()

            if line == "":
                send_line(player_socket, "ERROR Invalid command")
                print(f"Invalid command from {username}: blank line")
                continue

            parts = line.split()
            command = parts[0]
            args = parts[1:]
            
            if command != "REVEAL":
                send_line(player_socket, "ERROR Invalid command")
                print(f"Invalid command from {username}: {line}")
                continue
            
            if len(args) != 2:
                send_line(player_socket, "ERROR Invalid command")
                print(f"Invalid command from {username}: {line}")
                continue

            try:
                row = int(args[0])
                col = int(args[1])
            except ValueError:
                send_line(player_socket, "ERROR Invalid command")
                print(f"Invalid command from {username}: {line}")
                continue

            outgoing_message = None
            debug_message = None
            progress_debug_message = None

            progress_for_self = []
            progress_for_opponent = []


            final_message_for_self = None
            final_status_for_self = None
            final_message_for_opponent = None
            final_status_for_opponent = None

            should_exit = False

            with match_lock:
                if match_state["game_over"]:
                    print(f"{username} stopping GAME OVER")
                    break

                result = reveal_cell(
                    match_state["board"],
                    player["state"],
                    row,
                    col
                )

                if result["status"] == "safe":
                    if player["state"]["safe_revealed_count"] == match_state["safe_cell_total"]:

                        finalize_match(match_state, player_id, "cleared_safe_cells")
                    outgoing_message = f"RESULT SAFE {result['row']} {result['col']} {result['value']}"
                    debug_message = f"{username} revealed ({result['row']}, {result['col']}): SAFE {result['value']}"

                    your_safe_count = player["state"]["safe_revealed_count"]
                    opponent_safe_count = opponent["state"]["safe_revealed_count"]

                    progress_for_self = [
                        f"PROGRESS YOU {your_safe_count}",
                        f"PROGRESS OPPONENT {opponent_safe_count}"
                    ]
                    progress_for_opponent = [
                        f"PROGRESS YOU {opponent_safe_count}",
                        f"PROGRESS OPPONENT {your_safe_count}"
                    ]

                    progress_debug_message = (
                        f"{player['username']} progress:{your_safe_count} safe cells |"
                        f"{opponent['username']} progress:{opponent_safe_count} safe cells "
                    )
                elif result["status"] == "mine":
                    opponent_alive = opponent["state"]["alive"]


                    if opponent_alive:
                        finalize_match(match_state, opponent_id, "hit_mine")
                    else:
                        finalize_match(match_state, "tie", "tie")

                    outgoing_message = f"RESULT MINE {result['row']} {result['col']}"
                    debug_message = f"{username} revealed ({result['row']}, {result['col']}): MINE"
                    should_exit = True

                elif result["status"] == "error":
                    outgoing_message = f"ERROR {result['message']}"
                    debug_message = f"Invalid reveal from {username}: {result['message']}"

                if match_state["game_over"]:
                    if match_state["final_reason"] == "cleared_safe_cells":
                        if match_state["winner"] == player_id:
                            final_message_for_self = "MESSAGE You cleared all safe cells first."
                            final_status_for_self = "WIN"
                            final_message_for_opponent = "MESSAGE Opponent cleared all safe cells first."
                            final_status_for_opponent = "LOSE"
                        elif match_state["winner"] == opponent_id:
                            final_message_for_self = "MESSAGE Opponent cleared all safe cells first."
                            final_status_for_self = "LOSE"
                            final_message_for_opponent = "MESSAGE You cleared all safe cells first."
                            final_status_for_opponent = "WIN"

                    elif match_state["final_reason"] == "hit_mine":
                        if match_state["winner"] == player_id:
                            final_message_for_self = "MESSAGE Opponent hit a mine."
                            final_status_for_self = "WIN"
                            final_message_for_opponent = "MESSAGE You hit a mine."
                            final_status_for_opponent = "LOSE"
                        elif match_state["winner"] == opponent_id:
                            final_message_for_self = "MESSAGE You hit a mine."
                            final_status_for_self = "LOSE"
                            final_message_for_opponent = "MESSAGE Opponent hit a mine."
                            final_status_for_opponent = "WIN"

                    elif match_state["final_reason"] == "tie":
                        final_message_for_self = "MESSAGE Both players hit mines."
                        final_status_for_self = "TIE"
                        final_message_for_opponent = "MESSAGE Both players hit mines."
                        final_status_for_opponent = "TIE"

                    elif match_state["final_reason"] == "disconnect":
                        if match_state["winner"] == player_id:
                            final_message_for_self = "MESSAGE Opponent disconnected."
                            final_status_for_self = "OPPONENT_DISCONNECTED"
                        elif match_state["winner"] == opponent_id:
                            final_message_for_opponent = "MESSAGE Opponent disconnected."
                            final_status_for_opponent = "OPPONENT_DISCONNECTED"
                    should_exit = True

            if outgoing_message is not None:
                send_line(player_socket, outgoing_message)

            for message in progress_for_self:
                send_line(player_socket, message)

            for message in progress_for_opponent:
                send_line(opponent["socket"], message)

            if final_message_for_self is not None:
                send_line(player_socket, final_message_for_self)
            
            if final_status_for_self is not None:
                send_line(player_socket, final_status_for_self)

            if final_message_for_opponent is not None:
                send_line(opponent["socket"], final_message_for_opponent)
            
            if final_status_for_opponent is not None:
                send_line(opponent["socket"], final_status_for_opponent)

            if debug_message is not None:
                print(debug_message)

            if progress_debug_message is not None:
                print(progress_debug_message)

            if should_exit:
                break
    finally:
        try:
            player_socket.close()
        except OSError:
            pass

def main(): 
    #create socket 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(2)

        print(f" server on {HOST}:{PORT}")

        #-----------------------------------
        #player 1
        print("Waiting for player1")
        player1_socket, player1_address = server_socket.accept()
        #print(f"player 1 is at this address{player1_address}")
        

        send_line(player1_socket, "WAITING")
        player1_join = recv_line(player1_socket)
        #print(f"player 1 message{player1_join}")

        player1_parts = player1_join.split(maxsplit=1)
        if len(player1_parts) < 2 or player1_parts[0] != "JOIN" or player1_parts[1].strip() == "":
            print("Invalid JOIN from player 1")
            send_line(player1_socket, "ERROR Invalid command")
            try:
                player1_socket.close()
            except OSError:
                pass
            return

        player1_username = player1_parts[1].strip()
        
        #player 1 profile
        player1 = {
            "socket": player1_socket,
            "address": player1_address,
            "username": player1_username,
            "state": create_player_state()
        }



        #------------------------------------
        #player 2
        print("waiting for player2")
        server_socket.settimeout(JOIN_TIMEOUT)
        try:
            player2_socket, player2_address = server_socket.accept()
        except socket.timeout:
            print("Timed out waiting for player 2")
            send_line(player1_socket, "MESSAGE No second player joined")
            try:
                player1_socket.close()
            except OSError:
                pass
            return
        finally:
            server_socket.settimeout(None)

        #print(f"Player 2 address {player2_address}")

        player2_join = recv_line(player2_socket)
        #print(f"player 2 message{player2_join}")

        player2_parts = player2_join.split(maxsplit=1)
        if len(player2_parts) < 2 or player2_parts[0] != "JOIN" or player2_parts[1].strip() == "":
            print("Invalid JOIN from player 2")
            send_line(player2_socket, "ERROR Invalid command")
            try:
                player2_socket.close()
            except OSError:
                pass
            try:
                player1_socket.close()
            except OSError:
                pass
            return

        player2_username = player2_parts[1].strip()


        player2 = {
            "socket": player2_socket,
            "address": player2_address,
            "username": player2_username, 
            "state": create_player_state()
        }




        #------------------------------------
        #game
        board = create_board(ROWS, COLS, MINE_COUNT)
        safe_cell_total = count_safe_cells(board)

        match_state = {
            "board": board,
            "rows": ROWS,
            "cols": COLS,
            "mine_count": MINE_COUNT,
            "safe_cell_total": safe_cell_total,
            "players":{
                1: player1,
                2: player2
            },
            "game_over":False,
            "winner":None,
            "final_reason": None
        }
        match_lock = threading.Lock()


        print("match made")
        print(f"Player 1: {match_state['players'][1]['username']}")
        print(f"Player 2: {match_state['players'][2]['username']}")    
        print(f"Board Size {match_state['rows']}X{match_state['cols']}")
        print(f"Mine Count: {match_state['mine_count']}")
        print(f"Safe Cells: {match_state['safe_cell_total']}")

        start_message = f"START {match_state['rows']} {match_state['cols']} {match_state['mine_count']}"
        #info for players 
        send_line(match_state["players"][1]["socket"], start_message)
        send_line(match_state["players"][2]["socket"], start_message)

        thread1 = threading.Thread(
            target = handle_client, 
            args = (1, match_state, match_lock)
        )
        thread2 = threading.Thread(
            target = handle_client,
            args = (2, match_state, match_lock)
        )

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
    finally:
        try:
            server_socket.close()
        except OSError:
            pass


if __name__ == "__main__":
    main()