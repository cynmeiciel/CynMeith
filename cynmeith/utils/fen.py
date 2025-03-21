from cynmeith.utils.aliases import FENStr, FENError, PieceSymbol

def fen_parser(fen: FENStr, width: int, height: int, enclosures: list[str]=["'",'"'], delimiter: str="/") -> list[list[PieceSymbol]]:
    """
    Parse a FEN string and return a 2D list representing the board.
    Use enclosures to represent pieces with multiple characters.
    
    Notes:
        - FENStr can start with a "!" to indicate an empty board.
    """
    if not isinstance(fen, FENStr):
        raise FENError(f"Invalid FEN: {fen}")
    if fen.startswith("!"):
        return [[" " for _ in range(width)] for _ in range(height)]
    
    rows = fen.split(delimiter)
    if len(rows) != height:
        raise FENError(f"Invalid FEN: Expected {height} rows, but got {len(rows)}")
    
    board = []
    quote = False
    piece = ""
    for irow, row in enumerate(reversed(rows)):
        board_row = []
        for char in row:
            if char.isdigit():
                for _ in range(int(char)):
                    board_row.append(" ")
            elif char in enclosures:
                if quote:
                    board_row.append(piece)
                    piece = ""
                quote = not quote
            elif quote:
                piece += char
            else:
                board_row.append(char)
        if quote:
            raise FENError(f"Invalid FEN: Unmatched quote in row {row}")
        
        if len(board_row) != width:
            raise FENError(f"Invalid FEN: Expected {width} columns, but got {len(board_row)} at row {irow}")
        board.append(board_row)
    return board


def fen_deparser(board: list[list[PieceSymbol]], enclosure: str = '"', delimiter: str = "/") -> FENStr:
    """
    Deparse a 2D list representing the board and return a FEN string.
    No error handling.
    """
    rows = []
    for row in reversed(board):
        fen_row = ""
        count = 0
        for piece in row:
            if piece == " " or piece is None:
                count += 1
            else:
                if count:
                    fen_row += str(count)
                    count = 0
                if len(piece) > 1:
                    fen_row += enclosure + piece + enclosure
                fen_row += piece
        if count:
            fen_row += str(count)
        rows.append(fen_row)
    return delimiter.join(rows)


if __name__ == "__main__":
    fen = "r1b'cc'3r/p2pBpNp/n4n2/1p1NP2P/6P1/3P4/P1P1K3/q5b1"
    board = fen_parser(fen, 8, 8)
    for row in board:
        print(row)
        
    print(fen_deparser(board))
        
        