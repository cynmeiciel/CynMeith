# **Exist**

An abstract strategy game of controlled collapse for two players

## **INTRODUCTION**

Exist is a two-player abstract strategy game played on an 8×8 board. Players take turns placing and maneuvering their pieces under strict spatial restrictions. As the board fills, space becomes a scarce resource. Victory is achieved by forcing your opponent into a position where they have no legal actions.

## **COMPONENTS**

+ 1 8×8 grid game board.  
+ 8 Black pieces for Player 1  
+ 8 White pieces for Player 2

Note: Pieces have two sides, a black-colored side and a white-colored side

Each player has 8 pieces in their reserve at the start of the game. When gaining an opponent's piece, flip the piece to your color side before deciding to place it on the board because it is now your piece.

## **OBJECTIVE**

The game ends immediately when one player has no legal actions available on their turn.

## **DEFINITIONS**

**Empty Square**: A square with no piece.

**Unused Piece**: A piece still in a player's reserve (off the board).

**Adjacent / 8-Neighbor**: Any of the eight squares orthogonally or diagonally touching a given square.

**Line**: A continuous straight sequence of squares in one direction: a row, a column, or a diagonal of any length.

**Dispute Line**: A line that contains exactly two pieces total, one of each color.

## **GLOBAL RESTRICTIONS**

At all times—except during the specific capture actions described later—the board must obey both of the following rules. Any action that would result in a violation (after captures are resolved) is illegal and must be undone.

### **Line Restriction**

No row, column, or diagonal may contain more than 2 pieces (of any color).

### **Tile Restriction**

A piece may never occupy a square whose 8-neighbor area contains more than 2 pieces (of any color).

**Note: Both restrictions count all pieces on the board, regardless of ownership.**

## **SETUP**

1. Place the empty board between the two players.  
2. Each player takes all 8 pieces of their chosen color and places them in their reserve area off the board.  
3. The board begins completely empty.

## **ACTIONS**

On your turn, you may perform one of the following actions, subject to the turn structure rules below.

### **1\. Place**

* Requirement: You must have at least one unused piece in your reserve.  
* How to do it: Take an unused piece from your reserve and put it on any empty square that is legal according to both global restrictions (unless using Tile Capture, see "Capturing").

### **2\. Move**

* Requirement: Select one of your pieces already on the board.  
* How to do it: Move that piece to an adjacent (orthogonal or diagonal) empty square that is legal according to both global restrictions (unless using Tile Capture).

## **TURN STRUCTURE**

Your turn is classified as either a Capture Turn or a Non‑Capture Turn.

### **Capture Turn *(1 action only)***

* You perform exactly one action—a Place, Move.  
* This single action must result in the capture of at least one opponent piece

### **Non‑Capture Turn *(up to 2 actions)***

* You may perform one or two actions of your choice.  
* No captures are allowed during a Non‑Capture Turn.  
* If you take two actions, they must be of different types (e.g., Place then Move, or Move then Place)  
* You may end your turn after only one action if you wish.  
* 

## **CAPTURING**

Capturing is the only time you are permitted to temporarily ignore one of the global restrictions. You cannot capture your own pieces, if any of your actions cause captures of your pieces, the move is considered illegal and needs to be undone. There are two distinct capture methods.

### **A. Line Capture *(Ignores Line Restriction)***

Condition: You move one of your pieces onto a square that is in one or many Dispute lines that includes that square (diagonal, vertical and horizontal).

Effect: You ignore the Line Restriction for that landing square. After the movement, that opponent piece on that Dispute Line is captured and removed. You gain the opponent's captured piece and put them into your reserve.

Important: After removal, the entire board must still obey both restrictions. If any illegality remains, the move is illegal and must be undone.

### **B. Tile Capture *(Ignores Tile Restriction)***

Condition: Your action places or moves one of your pieces onto a square such that, before the action is fully resolved, the 8‑neighborhood of an opponent piece would contain more than 2 pieces (any color).

Effect: You temporarily ignore the Tile Restriction for the destination square. After the placement or movement, that opponent piece is captured and removed. You gain the opponent's captured piece and put them into your reserve.

Important: After removing the captured piece, every square on the board must again obey both global restrictions. If any square is found to violate a restriction, the action is illegal and must be undone.

**Note: A capture may remove one or more opponent pieces if multiple are affected simultaneously by the same action. In such cases, you gain all of their captured pieces. If a single Move action satisfies the conditions for both Line Capture and Tile Capture, all eligible opponent pieces are captured.**

## **Draw**

If all 16 pieces are placed on the board at the end of a player turn, the game ends in a draw immediately.

## **QUICK REFERENCE**

| Action | Capture Type Used | Restriction Ignored |
| :---- | :---- | :---- |
| Place | Tile Capture | Tile Restriction |
| Move | Tile and Line Capture | Tile and Line Restriction |

## 

| Turn Type | Actions Allowed | Captures Allowed |
| :---- | :---- | :---- |
| Capture Turn | 1 only | Yes (required) |
| Non‑Capture | 1-2 | No |

## **FREQUENTLY ASKED CLARIFICATIONS**

Q: What if a Dispute Line has more than two pieces?  
A: By the Line Restriction, no line may ever have more than two pieces. Therefore, a Dispute Line always contains exactly two pieces—one of each color.

Q: Does the captured piece count toward the neighbor total that triggers Tile Capture?  
A: Yes. The placement or movement increases the neighbor count, causing the opponent piece to exceed the limit of 2, which triggers the capture.

Q: After a capture, what if my own pieces now violate a restriction?  
A: The entire board is rechecked. If any violation exists, the move is illegal and must be retracted.

Q: Can I voluntarily ignore a restriction just to move somewhere, without capturing?  
A: No. Restrictions can only be ignored as part of a capture action. If no capture occurs, the move is illegal.  
