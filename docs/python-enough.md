# Python Enough for CynMeith

This guide is not a general Python course.

It teaches only the Python you need to start doing useful work in CynMeith:

- writing a piece
- checking the board
- adding a custom move rule
- attaching a side effect

If you can follow the examples here, you are already far enough to prototype games with this engine.

## Who This Guide Is For

This page is for you if:

- you are curious about making your own board-game rules
- you can read some code, but do not want a full Python textbook first
- you want the smallest possible set of ideas that unlock CynMeith

This page is not for advanced Python users. If you are already comfortable with classes, functions, and conditionals, you can skim this and move on to [Your First Custom Game](first-game.md).

## What You Need to Know First

You do not need all of Python.

You mostly need these ideas:

1. names and values
2. functions
3. `if` statements
4. `for` loops
5. classes
6. imports
7. returning `True`, `False`, or `None`

That is enough for a surprising amount of game logic.

## The Mental Model

Before syntax, understand the shape of the engine.

- A `Piece` decides whether its own movement shape is legal.
- A `Board` lets you inspect what is on the board.
- A `MoveManager` handles bigger rules that involve more than one piece.
- A `Game` ties everything together and handles turn flow.

When you write custom rules in CynMeith, you are usually doing one of two things:

- checking whether a move is allowed
- describing what extra should happen after a move succeeds

That is why the Python you need is mostly small checks and small classes.

## 1. Names and Values

In Python, you give a value a name with `=`.

```python
distance = 2
symbol = "S"
allowed = True
```

You will do this constantly in move logic:

```python
dr = new_position.r - self.position.r
dc = new_position.c - self.position.c
```

Here:

- `dr` means "change in row"
- `dc` means "change in column"

These two values are often enough to describe a move.

## 2. Functions

A function is a named block of code that does one job.

```python
def is_forward_step(start, end):
    dr = end.r - start.r
    dc = end.c - start.c
    return dr == 1 and dc == 0
```

Important parts:

- `def` starts a function
- the indented block is the function body
- `return` sends the result back

In CynMeith, functions often return:

- `True` if something is allowed
- `False` if something is not allowed
- `None` if a move cannot be resolved

## 3. `True`, `False`, and `None`

These three values matter a lot in the engine.

- `True`: yes, this condition holds
- `False`: no, it does not
- `None`: there is no usable value here

Examples:

```python
return True
return False
return None
```

Typical CynMeith usage:

```python
piece = self.board.at(move.start)
if piece is None:
    return None
```

That means: "There is no piece at the starting square, so this move is not a real move."

## 4. `if` Statements

An `if` statement lets you make decisions.

```python
if dr == 1:
    return True
return False
```

Most piece logic is a sequence of small filters:

```python
def is_valid_move(self, new_position, board):
    if board.is_allied(new_position, self.side):
        return False
    if not self.position.is_diagonal(new_position):
        return False
    if not board.is_empty_line(self.position, new_position, Coord.is_diagonal):
        return False
    return True
```

This reads as:

1. if the target has an allied piece, reject it
2. if the move is not diagonal, reject it
3. if the path is blocked, reject it
4. otherwise allow it

This style is common in CynMeith because it is easy to read and debug.

## 5. `for` Loops

A `for` loop repeats something.

```python
for number in (1, 2, 3):
    print(number)
```

In CynMeith, loops often generate candidate moves:

```python
for delta in (Coord(-1, 0), Coord(1, 0), Coord(0, -1), Coord(0, 1)):
    position = self.position + delta
    if board.is_in_bounds(position):
        yield position
```

That means:

- look at four directions
- build a new position for each one
- only keep positions that are still on the board

## 6. Imports

Imports let you use code from elsewhere.

A common start for CynMeith pieces looks like this:

```python
from cynmeith import Piece
from cynmeith.utils import Coord
```

A common start for a manager looks like this:

```python
from cynmeith import MoveManager
from cynmeith.utils import Move
```

You do not need to understand the full import system. At this stage, just read it as "I need these tools from CynMeith."

## 7. Classes

In CynMeith, pieces are classes.

A class is a blueprint. A piece object is one actual piece created from that blueprint.

Here is a minimal piece:

```python
from cynmeith import Piece
from cynmeith.utils import Coord


class Scout(Piece):
    symbol = "S"

    def is_valid_move(self, new_position: Coord, board) -> bool:
        dr = abs(new_position.r - self.position.r)
        dc = abs(new_position.c - self.position.c)
        return dr + dc == 2
```

Read this as:

- `class Scout(Piece)`: make a new piece type based on `Piece`
- `symbol = "S"`: use `S` as the piece symbol
- `def is_valid_move(...)`: define how this piece moves

## Understanding `self`

`self` means "this specific piece".

So:

- `self.position` means this piece's current position
- `self.side` means this piece's side

You do not create `self`. Python passes it automatically inside methods.

## Type Hints: Helpful, Not Magical

You will often see code like this:

```python
def is_valid_move(self, new_position: Coord, board) -> bool:
```

The `: Coord` and `-> bool` parts are type hints.

They are there to help humans and tools understand the code. They do not
change the basic logic of the function.

At first, you can read that line as:

"This method receives a `Coord` and returns `True` or `False`."

## The Most Useful Board Questions

When writing rules, these are the most useful board methods to know first:

- `board.at(position)`
- `board.is_empty(position)`
- `board.is_enemy(position, side)`
- `board.is_allied(position, side)`
- `board.is_in_bounds(position)`
- `board.is_empty_line(start, end, ...)`

Examples:

```python
piece = board.at(new_position)
```

That asks: what piece is on this square?

```python
if board.is_empty(new_position):
    ...
```

That asks: is the square empty?

```python
if board.is_enemy(new_position, self.side):
    ...
```

That asks: is there an enemy piece there?

## Coordinates

Positions are represented by `Coord`.

```python
Coord(2, 3)
```

That means:

- row `2`
- column `3`

Useful coordinate helpers include:

- `Coord.up()`
- `Coord.down()`
- `Coord.left()`
- `Coord.right()`
- `position.is_diagonal(other)`
- `position.is_orthogonal(other)`
- `position.manhattan_to(other)`
- `position.chebyshev_to(other)`

Example:

```python
if self.position.manhattan_to(new_position) == 1:
    return True
```

That means the target is exactly one orthogonal step away.

## Writing Your First Real Piece

Here is a clearer example piece:

```python
from cynmeith import Piece
from cynmeith.utils import Coord


class Guard(Piece):
    symbol = "G"

    def is_valid_move(self, new_position: Coord, board) -> bool:
        if board.is_allied(new_position, self.side):
            return False
        return self.position.manhattan_to(new_position) == 1

    def iter_move_candidates(self, board):
        for delta in (Coord.up(), Coord.down(), Coord.left(), Coord.right()):
            position = self.position + delta
            if board.is_in_bounds(position):
                yield position
```

This piece:

- cannot land on an allied piece
- moves one orthogonal step
- only generates nearby candidates

That is already enough to build a simple game around.

## Why `iter_move_candidates(...)` Exists

There are two different jobs:

1. deciding whether a specific move is legal
2. generating possible destinations to check

`is_valid_move(...)` handles job 1.

`iter_move_candidates(...)` helps with job 2.

Without `iter_move_candidates(...)`, a piece may check the whole board. That is fine for tiny prototypes, but it is often cleaner to generate only nearby or ray-based positions.

For example:

- a knight-like piece only needs a few offsets
- a rook-like piece should scan in straight lines
- a king-like piece only needs adjacent squares

## Sliding Pieces

Sliding pieces usually use board traversal helpers.

```python
def iter_move_candidates(self, board):
    for direction in (Coord.up(), Coord.down(), Coord.left(), Coord.right()):
        for position in board.iter_positions_towards(self.position + direction, direction):
            yield position
            if board.at(position) is not None:
                break
```

This means:

- look outward in one direction
- keep yielding squares
- stop when you hit a blocker

That pattern is useful for rook-like, bishop-like, and queen-like pieces.

## When a Piece Is Not Enough

Some rules are bigger than one piece.

Examples:

- castling
- en passant
- promotions
- "you may capture without moving"
- "this move is illegal if your king is exposed"

Those belong in a `MoveManager`.

## Writing a Move Manager

Here is the standard shape:

```python
from cynmeith import MoveManager
from cynmeith.utils import Move


class MyManager(MoveManager):
    def resolve_move(self, move: Move) -> Move | None:
        piece = self.board.at(move.start)
        if piece is None:
            return None

        if self.board.is_allied(move.end, piece.side):
            return None

        if not piece.is_valid_move(move.end, self.board):
            return None

        return move
```

Read this as:

- find the moving piece
- reject the move if there is no piece
- reject the move if the destination contains an allied piece
- reject the move if the piece itself says the geometry is illegal
- otherwise accept the move

## What `resolve_move(...)` Really Does

`resolve_move(...)` does not only validate.

It can also enrich the move with extra information.

That is how special behavior gets attached to a move before it is applied.

For example:

```python
extra = dict(move.extra_info or {})
extra["promotion"] = "Q"
return Move(move.start, move.end, move.move_type, extra)
```

Or:

```python
extra = dict(move.extra_info or {})
extra["effects"] = EffectPresets.capture(target)
return Move(move.start, move.end, move.move_type, extra)
```

## Effects

Effects mean: "After the move succeeds, also do this."

This is the engine's way to represent irregular consequences.

Example:

```python
from cynmeith import EffectPresets
from cynmeith.utils import Move


def with_capture(move: Move, target: Coord) -> Move:
    extra = dict(move.extra_info or {})
    extra["effects"] = EffectPresets.capture(target)
    return Move(move.start, move.end, move.move_type, extra)
```

This function takes a move and a target square, and returns a new move that has the same start and end, but also includes an effect to capture the piece at the target square.

## Stationary or Skill Moves

Sometimes a piece does something without moving.

For that kind of move, the manager can attach:

- `move_actor = False`
- one or more effects

That lets the board state change even though the moving piece stays in place.

This is useful for:

- abilities
- strikes
- summons
- traps

## Stateful Pieces

Some pieces need memory.

Example:

```python
class Runner(Piece):
    symbol = "R"

    def __init__(self, side, position):
        super().__init__(side, position)
        self.has_moved = False

    def move(self, new_position: Coord) -> None:
        self.position = new_position
        self.has_moved = True
```

This is appropriate when the state belongs to that one piece.

Good examples:

- `has_moved`
- remaining jump count
- transformed state

Bad examples:

- whose turn it is
- game phase
- player score

Those belong elsewhere.

## A Simple Rule-Building Pattern

A lot of CynMeith code follows this pattern:

```python
def is_valid_move(self, new_position: Coord, board) -> bool:
    if first_bad_condition:
        return False
    if second_bad_condition:
        return False
    if third_bad_condition:
        return False
    return True
```

This is worth copying.

It is:

- easy to read
- easy to debug
- easy to extend later

Do not feel like you need a clever one-line expression for every rule.

## Common Mistakes

### 1. Putting everything in one giant piece method

If the rule depends on other pieces, turn state, or special consequences, it
often belongs in a manager instead.

### 2. Mutating the board during validation

Try to validate first, then attach effects, then let the engine apply the move.

### 3. Forgetting bounds checks

When generating positions manually, use `board.is_in_bounds(position)`.

### 4. Mixing piece-local and game-wide state

If the state belongs to the whole game, do not put it on a piece.

### 5. Over-optimizing too early

A clear rule is better than a clever rule while you are still discovering the
game.

## A Tiny Practice Path

If you want to build confidence, try these in order:

1. make a piece that moves one step orthogonally
2. make a piece that moves diagonally any distance
3. make a piece that cannot capture, only move to empty squares
4. make a manager rule that blocks allied captures
5. make a manager rule that adds a capture effect to a special move

If you can do those five things, you are already beyond the beginner stage for
this engine.

## What You Can Ignore For Now

You do not need to master all of this before building a game:

- advanced typing
- decorators
- inheritance beyond subclassing `Piece`
- metaclasses
- async code
- packaging theory

Those are not the bottleneck for CynMeith work.

## What To Read Next

Once this guide feels comfortable, continue with:

- [Your First Custom Game](first-game.md)
- [Extending the Engine](extending.md)
- [Examples Guide](examples.md)
- [API Reference](api.md)

