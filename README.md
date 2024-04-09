# ChessOnline

ChessOnline is a simple chess game with both an offline mode and a potential for online play, designed using PyGame, a set of Python modules designed for writing video games. The game offers an easy-to-use interface and classic chess gameplay, making it accessible for chess enthusiasts and those looking to learn the basics of the game.

## Technology Stack
- Python: High-level programming language used for game logic.
- PyGame: Cross-platform set of Python modules designed for writing video games; handles rendering, event handling, and more.
- Sys: System-specific parameters and functions module in Python used for script termination.
- Random: Python module providing access to random number generators.
- Time: Python module providing access to time-related functions.

## Game Modes
- **Offline Mode**: Play against a friend on the same computer or against a simple AI that makes random moves.
- **Bot Mode (Only one side automated)**: Play against a computer bot. This mode is for practicing your chess moves and strategy.

## How to Play
1. **Start the Game**: Run the `ChessOnline.py` script to initiate the game. PyGame will start and the game window will open.
2. **Choose Player Color**: Select whether you want to play as White or Black. This option is given at the start of the game.
3. **Choose Game Mode**: Decide whether you want to play in bot mode or not. Bot mode allows you to play against a simple AI.
4. **Making a Move**: Click on a chess piece to select it, and then click another square to move it. If the move is legal, the piece will move to the desired location.
5. **Check and Checkmate**: The game will automatically detect check and checkmate situations, highlighting the king in danger and ending the game if it's checkmate.
6. **End the Game**: The game concludes when one player checkmates the other player's king, resulting in a win. In case of a stalemate, the game will display a corresponding message.

## Board Setup
The board set up corresponds to the standard chess rules:
- Pawns are placed on the second and seventh ranks.
- Rooks are located at the corners of the board.
- Knights are placed beside the rooks.
- Bishops sit next to the knights.
- The queen occupies the remaining square of her own color.
- The king takes the last square left open in the back rank.

## Running the Game
1. Ensure Python and PyGame are installed in your environment.
2. Clone or download the game's code to your local machine.
3. Navigate to the directory containing the game script.
4. Execute `python ChessOnline.py` to run the game.

## Future Development
Potential future updates might include:
- Implementation of additional AI difficulty levels.
- Expanding the online functionality for remote play against other players.
- Adding chess puzzles and tutorials for beginners.
- Providing options for time-controlled games (e.g., blitz, rapid).

Enjoy your game with ChessOnline, offering a classic chess experience with a modern digital touch!
