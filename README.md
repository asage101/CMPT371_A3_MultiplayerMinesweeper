# CMPT 371 A3 Socket Programming ``` Minesweeper Race ```
**Course:** CMPT 371 - Data Communications & Networking

**Instructor:** Mirza Zaeem Baig

**Semester:** Spring 2026

***RUBRIC NOTE: As per submission guidelines, only one group member will submit the link to this repository on Canvas.*** 

---
## Group Members
| Name | Student ID | Email |
|------|-----------|------|
| Alina Pharis | 301551508  | asp29@sfu.ca |
| Tushar Singh | 301560473 | tsa156@sfu.ca |

---
## Project Overview
This project is a multiplayer Minesweeper race game built using Python’s Socket API (TCP). It allows two clients to connect to a central server, receive the same hidden mine layout, and race independently to reveal all safe cells first.

Each player plays on their own visible board, but both share the same underlying mine configuration. The server handles all game logic, validation, and win conditions, ensuring fairness and preventing any client-side cheating.

The game ends when:
- A player reveals all safe cells (win)
- A player hits a mine (loss)
- Both players hit mines (tie)
- A player disconnects (other player wins by default)

### Configuration

The project uses a `config.py` file to store all key settings, including:

- Network settings (`HOST`, `PORT`)
- Game settings (`ROWS`, `COLS`, `MINE_COUNT`)
- Join timeout (`JOIN_TIMEOUT`)

These values are imported by both the server and client, allowing the game setup to be easily modified without changing the main code. The default values are used for testing and grading.
---
## System Limitations & Edge Cases

While building this project, we had to deal with a few common networking issues and edge cases:

### Handling Multiple Clients
We used Python’s `threading` module so each client runs in its own thread. Both threads share the same game state, which is protected using a lock to avoid conflicts.

One limitation of this approach is that threads don’t scale very well if there were a lot of players. For a larger system, something like async I/O or a thread pool would be a better choice.

### TCP Message Handling
Since TCP is a stream-based protocol, messages don’t always arrive cleanly one at a time — they can be split up or combined together.

To handle this, we used newline (`\n`) as a delimiter and buffered incoming data until we had a full message before processing it.

### Input Validation
The server is responsible for validating all inputs to keep the game consistent. It checks for:
- invalid commands → `ERROR Invalid command`
- out-of-bounds moves → `ERROR Invalid move`
- revealing the same cell twice → `ERROR Cell already revealed`

The client does some basic input checking, but the server is always treated as the source of truth.

### Disconnect Handling
If a player disconnects during the game, the other player automatically wins.

If a disconnect happens before the game starts (while waiting for a second player), the server handles it gracefully and shuts down the session without crashing.

### Join Timeout
If a second player doesn’t connect within a set amount of time, the first player is notified and the session is closed.

---
## Video Demo
Watch the demo here: 

---
## Prerequisites (Fresh Environment)

To run this project, you need:

- Python 3.10 or higher
- No external libraries required (uses standard libraries: `socket`, `threading`, `sys`, `os`)

Run in:
- VS Code or any terminal

---

## Step-by-Step Run Guide

> **Important:** These commands can be copy and pasted directly 

### Step 1: Start the Server

Open a terminal and navigate to the project root folder.

Run:

```bash
python server/server.py
```
**Expected Output**
```
server on 127.0.0.1:5000
Waiting for player1
```
> The server uses default settings defined in `config.py` (eg. port 500, number of mines, etc)
### Step 2: Connect Player 1

Open a **new terminal** (leave the server running).

Run:

```bash
python client/client.py
```

Enter a username when prompted.

Expected output:

```
WAITING
```
### Step 3: Connect Player 2

Open a **third terminal**.

Run:

```bash
python client/client.py
```

Enter a username.

Expected output:

```
Game started!
```

---

### Step 4: Gameplay

Players enter moves in the format:

```
row col
```

Example:

```
3 5
```

Each move reveals a cell:
- Safe → shows number
- Mine → game ends

The game continues until:
- One player clears all safe cells
- A player hits a mine
- A disconnect occurs

---

## 6. Technical Protocol Details

This project uses a simple line-based protocol over TCP.

### Client → Server
```
JOIN <username>
REVEAL <row> <col>
```

### Server → Client
```
WAITING
START <rows> <cols> <mines>
RESULT SAFE <row> <col> <value>
RESULT MINE <row> <col>
PROGRESS YOU <count>
PROGRESS OPPONENT <count>
MESSAGE <text>
WIN
LOSE
TIE
OPPONENT_DISCONNECTED
ERROR <message>
```



---

### Project Structure

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
    ├── minesweeper.py
    └── __init__.py
```

## Academic Integrity & References
**Code Origin**
- Code implementation was written by the group 
- Basic socke structure was inspired by course materials 

**GenAI Usage**
- ChatGPT was used to debug socket behavior, structuring message protocol, and improving README clarity

**References**
