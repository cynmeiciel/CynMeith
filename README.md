# CynMeith - A Board Game Engine  
It's pronounced **/'siːn.meɪt/**, by the way

CynMeith is a small, flexible board-game framework for prototyping turn-based games and custom rule sets.

After cooking some spaghetti that made me refuse to look at them again, I decided to write a brand new one, with my brand new brain.

**Practice makes perfect**

This might be quite overengineering with a bunch of design patterns and extra classes, but I think it is okay.

## Goals
This project is designed and expected to be easily configurable, modular and extendable, so that it can be a foundation for more complex games.
- **Modularity**: The game is designed to be modular, allowing for easy replacement or extension.
- **Configurability**: The game can be configured using external configuration files, making it easy to change the setup without modifying the code.
- **Extendability**: New rules, pieces, and features can be added with minimal changes to the existing codebase.

### Task to do: Finish the engine, make it playable first, then implement chess, and then improve the performance last.

It ships with Tk examples for chess and xiangqi.

## What to look at
- API and usage notes: [docs/api.md](docs/api.md)
- Example launchers: [examples/tk_demo.py](examples/tk_demo.py)