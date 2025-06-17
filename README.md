# DSprojectSeeu
A distributed System project 
Project Documentation: Distributed Tic Tac Toe Game

Project Description
This project implements a simple two-player Tic Tac Toe game that runs over a network using socket communication. The game allows two autonomous agents (players), which can be human users running client applications or automated agents, to compete by contending for shared game state — the Tic Tac Toe board. The system supports real-time updates to the shared state (game moves) between the players.

The game features:

A distributed system architecture where the game state is synchronized between two nodes: a server node and a client node.

Real-time bidirectional communication using TCP sockets for reliable message passing.

A graphical user interface (GUI) for user interaction, built using the Tkinter framework.

Fault tolerance by detecting disconnections. The server can accept a new player to continue the game even if the current client disconnects.

The game state and user turns are consistently updated and shared across network nodes, ensuring both players have the current view of the board.

Relation to Distributed Systems Concepts
Multiple Autonomous Agents: The two players (server and client) act as independent agents performing moves concurrently in a shared environment.

Shared State Management: The Tic Tac Toe board represents a shared state distributed between the two nodes, requiring synchronization after each move.

Communication & Coordination: TCP sockets provide a communication channel enabling message exchange for moves and game control signals, illustrating basic distributed coordination.

Fault Tolerance: The server detects if a client disconnects unexpectedly and can accept a new client, maintaining system availability despite node failures.

Distributed State Consistency: Both nodes maintain and update the game board consistently by exchanging move information, demonstrating a simple form of state replication and consistency management.

Client-Server Model: The system follows a client-server architecture where the server manages incoming connections and coordinates gameplay, a foundational pattern in distributed applications.
