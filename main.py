from board import Board


def main():
    board = Board(headless=False)

    while True:
        word = input()
        board.guess(word)
        print(board)


if __name__ == "__main__":
    main()
