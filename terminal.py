from game.board import Board
from game.utils import (
    posFromEncoding,
    endcodingFromPos,
    UNICODE_PIECE_SYMBOLS as UP,
    Color,
)
from bots.randomBot import RandomBot
import sys

HELP_MESSAGE = """Commands to use game
  > [player color tag] [srcPos] [destPos]
                - player moves piece. eg.
        > w e7 e5
        > b e2 e3
  > m [piecePos]
                - give possible moves
  > h             - help
  > q             - quit"""


class Logs:
    def __init__(self) -> None:
        self.logs = []
        self.limit = 16

    def add(self, msg: "str"):
        self.logs = self.logs + msg.split("\n")
        if len(self.logs) > 16:
            self.logs = self.logs[-16:]

    def lgs(self):
        return self.logs


bot = RandomBot()
withBot = True

board = Board()
turn = "w"
logs = Logs()


def log(msg: str):
    global logs
    logs.add(msg)


def mergeMessages(boardStr: "str", logs: "list[str]"):
    newMsg = boardStr.split("\n")
    n = len(newMsg)
    for i in range(n - 1, -1, -1):
        try:
            newMsg[i] += "\t" + logs[i - n]
        except:
            break
    return "\n".join(newMsg)


def makeMove(inps):
    global turn
    frm = posFromEncoding(inps[1])
    if frm == None:
        log("\033[91minvalid encoding" + "\033[0m")
        return
    srcPis = board.getPiece(frm)
    if srcPis == None:
        log("\033[91mNo piece on source position" + "\033[0m")
        return
    if str(srcPis)[0] != turn:
        log("\033[91mIllegal move " + str(srcPis) + "\033[0m")
        return
    to = posFromEncoding(inps[2])
    if to == None:
        log("\033[91minvalid encoding" + "\033[0m")
        return
    valid, kingDied = board.movePieceFromTo(frm, to)
    if not valid:
        log("\033[91mIllegal move\033[0m")
        return
    log(
        "\033[94m"
        + str(srcPis)
        + " moved from "
        + inps[1]
        + " to "
        + inps[2]
        + "\033[0m"
    )
    turn = "b" if turn == "w" else "w"
    return kingDied


def givePossibleMoves(inps):
    pos = posFromEncoding(inps[1])
    if pos == None:
        log("\033[91minvalid encoding" + "\033[0m")
        return
    piece = board.getPiece(pos)
    if piece == None:
        log("\033[91mno piece on " + inps[1] + "\033[0m")
        return
    legalMoves, illegalMoves = piece.possibleMoves(board)
    lMoves = list(map(endcodingFromPos, legalMoves))
    ilMoves = list(map(endcodingFromPos, illegalMoves))
    log(str(piece) + " ~ legal:" + str(lMoves) + "\n   illegal:" + str(ilMoves))


def showDeaths():
    log("  ".join(list(map(lambda x: UP.get(x, ""), [str(a) for a in board.deaths]))))


def help():
    log(HELP_MESSAGE)


def loop():
    while True:
        print("\033[2J" + "\033[H", end="")
        print(mergeMessages(str(board), logs.lgs()))
        print(("White" if turn == "w" else "Black") + "'s turn\n> ", end="")
        if withBot and turn == "b":
            print("Bot thinking...")
            frm, to = bot.giveMove(board, Color.BLACK)
            frm, to = endcodingFromPos(frm), endcodingFromPos(to)
            inp = "b " + frm + " " + to
            log("\n" + inp)
            makeMove(inp.split(" "))
            continue
        inp = input()
        log("\n> " + inp)
        inps = inp.split(" ")
        if inps[0] == "b" or inps[0] == "B":
            if turn == "w":
                log("\033[91mwrong turn" + "\033[0m")
                continue
            if makeMove(inps):
                log("\033[92m Black team player won" + "\033[0m")
                break
        elif inps[0] == "w" or inps[0] == "W":
            if turn == "b":
                log("\033[91mwrong turn" + "\033[0m")
                continue
            if makeMove(inps):
                log("\033[92m White team player won" + "\033[0m")
                break
        elif inps[0] == "h" or inps[0] == "H":
            help()
        elif inps[0] == "m" or inps[0] == "M":
            givePossibleMoves(inps)
        elif inps[0] == "d" or inps[0] == "D":
            showDeaths()
        elif inps[0] == "q" or inps[0] == "Q":
            log("\033[93mquiting game" + "\033[0m")
            break
    print("\033[2J" + "\033[H" + mergeMessages(str(board), logs.lgs()))


def main():
    board.resetBoard()
    help()
    print(chr(27) + "[2J")
    loop()


if __name__ == "__main__":
    for arg in sys.argv:
        if arg == "-p":
            withBot = False
    main()
