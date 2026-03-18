# Minesweeper Race 

## Project Description 
Minesweeper race is a 2 player socket programming game built in Python. Both players connect to the same server and play on the same Minesweeper board layout, but each player reveals cells on their own seperate client server. The players race to reveal safe cells as quickly as possible. The server tracks both players progress and determines the final outcome. 

Win Conditions:
- Revealing all safe cells first 
- Opponent hitting a mine 
- Opponent disconnecting 

## Architecture 
This project uses client-server architecture
- the server is responsible for creating the board, accepting 2 client connections, tracking the game states, and deciding the game's outcome 
- the clients are responsible for connecting both players to the server, sending inputs, and displaying the current board and progress for each player
- the server uses threading to allow both players to play at the same time 
- Both players play on the same board but each has their own: revealed cells, progress count, and "alive/dead" state

## Features

## Project Structure
```
CMPT371_A3_MinesweeperRace/
│
├── config.py
├── README.md
├── requirements.txt
│
├── client/
│   └── client.py
│
├── server/
│   └── server.py
│
└── game/
    └── minesweeper.py
    └── __init__.py 
```

## Requirements 
This project uses Python 3

### Python Standard Library Modules: 
- socket
- threading
- random
- sys
- os


## How to Run the Project 
Run everything from the project root folder 
### How to Run the Server
Open a terminal in the project root and run: 

`python server/server.py` 

### How to Run Client 1 (Player 1)
In a second terminal run
`python client/client.py` 
Enter your username when asked.

### How to Run Client 2 (Player 2)
In a third terminal run
`python client/client.py` 
Enter your username when asked.

Once both players have connected, the game will begin automatically. 

## How to Play 
Each client has: 
- the board 
- their progress
- their opponents progress
- record of previous results

To make a move type input :
`row col`  
Example: 
`3 5 ` 
which would reveal the cell at row 3 column 5

### Board Symbols 
`.` : hidden cell

`0-8` : safe cell, the number refers to the number of adjacent mines

`*` : mine

### Game Rules
- both players are playing copies of the same hidden board 
- Both players are playing at the same time there are no "turns"
- Each player tracks progress individually 
Player loses: 
- if they hit a mine
Player wins:
- if they reveal all safe cells first 
- opponent hits mine 
- opponent disconnects 

