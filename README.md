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

---
## System Limitations & Edge Cases

As required by the project specifications, the following limitations and edge cases were considered:

### Handling Multiple Clients Concurrently
- **Solution:** Python’s `threading` module is used. Each client is handled in a separate thread while sharing a locked match state.
- **Limitation:** Thread-based design does not scale well for large numbers of clients. A production system would use async I/O or thread pools.

### TCP Stream Buffering
- **Solution:** TCP is a continuous stream, so messages may arrive combined or split. We solved this by using newline (`\n`) delimiters and buffering input until a full line is received.

### Input Validation & Robustness
- **Solution:** The server validates all commands strictly:
  - Invalid commands → `ERROR Invalid command`
  - Out-of-bounds moves → `ERROR Invalid move`
  - Duplicate reveals → `ERROR Cell already revealed`
- **Limitation:** The client performs light validation, but the server remains the source of truth.

### Disconnect Handling
- If a player disconnects mid-game, the opponent automatically wins.
- If a disconnect happens during waiting, the server cleans up without crashing.

### Join Timeout
- If a second player does not connect within a fixed timeout, the first player is notified and the session closes.

---
## Video Demo
---
## Prerequisites (Fresh Environment)

To run this project, you need:

- Python 3.10 or higher
- No external libraries required (uses standard libraries: `socket`, `threading`, `sys`, `os`)

Optional:
- VS Code or any terminal

---

## Step-by-Step Run Guide

> **Important:** The grader should be able to copy-paste these commands.

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

All messages are newline-delimited (`\n`).

---

## 7. Project Structure

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