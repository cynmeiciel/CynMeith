def fen_parser(fen: str) -> list[list[str]]:
    """
    Parse a FEN string and return a 2D list representing the board.
    """
    rows = fen.split("/")
    board = []
    for row in rows:
        board_row = []
        for char in row:
            if char.isdigit():
                for _ in range(int(char)):
                    board_row.append(" ")
            else:
                board_row.append(char)
        board.append(board_row)
    return board


if __name__ == "__main__":
    fen = "r1bk3r/p2pBpNp/n4n2/1p1NP2P/6P1/3P4/P1P1K3/q5b1"
    board = fen_parser(fen)
    for row in board:
        print(row)