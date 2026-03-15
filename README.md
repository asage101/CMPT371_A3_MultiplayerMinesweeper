## Project Description 

This project is a two-player networked Minesweeper race built using Python socket programming 
Both players connect to the same server and recieve the same 8 * 8 board with the same 10 mine locations
Each player plays on their own board independently, and the goal is to reveal all safe cells before the other player while avoiding mines 
The project uses client server architecture. The server is responsible for creating the shared mine layout, managing player connections, validating moves, trakcing game state, and declaring the result

## Game Rules

- The game supports exactly 2 players.
- The board size is 8 x 8.
- Each board contains 10 mines.
- Both players receive the same mine layout.
- Players reveal cells independently on their own copy of the board.
- One player’s actions do not affect the other player’s board.
- If a player reveals a mine, they immediately lose.
- If a player reveals all safe cells, they win.
- If one player loses and the other is still alive, the other player wins.
- If both players reveal mines, the game ends in a tie.
- If one player disconnects during the game, the other player wins by default.

## Limitations

- The game supports only 2 players.
- The board size and mine count are fixed at 8x8 with 10 mines.
- The game uses a command-line interface only.
- Zero-value cells do not automatically expand.
- Players cannot place flags.
- If a client disconnects unexpectedly, the server ends the match and declares the other player the winner.
- The project is designed for local testing or simple direct network play and does not include matchmaking, persistent accounts, or replay storage.