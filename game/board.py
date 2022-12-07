from typing import TYPE_CHECKING, Callable

from .utils import Pos, Color, UNICODE_PIECE_SYMBOLS as UP
from .pieces import Pawn, Knight, Bishop, Rook, Queen, King, PossibleMoves

if TYPE_CHECKING:
    from .pieces import Piece

CLASS_MAP: "dict[str, type[Piece]]" = {
    "P": Pawn,
    "R": Rook,
    "N": Knight,
    "B": Bishop,
    "Q": Queen,
    "K": King,
}


class Board:
    def __init__(self) -> None:
        self.board: "list[list[Piece|None]]" = [
            [None for _ in range(8)] for _ in range(8)
        ]
        self.deaths: "list[Piece]" = []
        self.checked: "None| Color" = None

        pass

    def resetBoard(self) -> None:
        # empty spaces
        for j in range(2, 5):
            for i in range(8):
                self.board[j][i] = None
        # pawns
        for i in range(8):
            self.createPiece(Pawn, Color.BLACK, i, 1)
            self.createPiece(Pawn, Color.WHITE, i, 6)

        # knites
        self.createPiece(Knight, Color.BLACK, 1, 0)
        self.createPiece(Knight, Color.BLACK, 6, 0)
        self.createPiece(Knight, Color.WHITE, 1, 7)
        self.createPiece(Knight, Color.WHITE, 6, 7)

        # bishops
        self.createPiece(Bishop, Color.BLACK, 2, 0)
        self.createPiece(Bishop, Color.BLACK, 5, 0)
        self.createPiece(Bishop, Color.WHITE, 2, 7)
        self.createPiece(Bishop, Color.WHITE, 5, 7)

        # rook
        self.createPiece(Rook, Color.BLACK, 0, 0)
        self.createPiece(Rook, Color.BLACK, 7, 0)
        self.createPiece(Rook, Color.WHITE, 0, 7)
        self.createPiece(Rook, Color.WHITE, 7, 7)

        # queen
        self.createPiece(Queen, Color.BLACK, 3, 0)
        self.createPiece(Queen, Color.WHITE, 3, 7)

        # king
        self.createPiece(King, Color.BLACK, 4, 0)
        self.createPiece(King, Color.WHITE, 4, 7)
        self.deaths.clear()
        self.checked = None

    def movePieceFromTo(
        self, src: "Pos", dest: "Pos", getInput: "Callable[[str],str]"
    ) -> "tuple[bool, bool]":
        srcPiece = self.getPiece(src)
        # check in possible moves
        if srcPiece == None:
            return False, False
        legalMoves, _ = srcPiece.possibleMoves(self)
        if dest not in legalMoves:
            return False, False

        # Castling
        if isinstance(srcPiece, King):
            if dest == src.move(-2, 0) or dest == src.move(2, 0):
                self.castlingMove(srcPiece, src, dest)
                if len(self.getAllPossibleMoves(srcPiece.color.GetOpp())) == 0:
                    return True, True
                return True, False

        destPiece = self.getPiece(dest)
        if destPiece == None:
            # pawn promotion
            if self.checkPawnPromotion(srcPiece, dest):
                return self.pawnPromotionMove(src, dest, getInput)
            self.setPiece(srcPiece, dest)
            self.removePiece(src)
            srcPiece.moveTo(dest)
            self.updateCheck(srcPiece.color)
            if len(self.getAllPossibleMoves(srcPiece.color.GetOpp())) == 0:
                return True, True
            return True, False
        if destPiece.color != srcPiece.color:
            isKing = isinstance(destPiece, King)
            # pawn promotion
            if not isKing and self.checkPawnPromotion(srcPiece, dest):
                return self.pawnPromotionMove(src, dest, getInput)
            self.killPiece(dest)
            self.setPiece(srcPiece, dest)
            self.removePiece(src)
            srcPiece.moveTo(dest)
            self.updateCheck(srcPiece.color)
            if len(self.getAllPossibleMoves(srcPiece.color.GetOpp())) == 0:
                return True, True
            return True, isKing
        return False, False

    def castlingMove(self, srcPiece: "Piece", src: "Pos", dest: "Pos"):
        if dest == src.move(2, 0):
            self.setPiece(srcPiece, dest)
            self.removePiece(src)
            srcPiece.moveTo(dest)

            rookPos = src.move(3, 0)
            rook: Rook = self.getPiece(rookPos)  # type: ignore
            self.setPiece(rook, src.move(1, 0))
            self.removePiece(rookPos)
            rook.moveTo(src.move(1, 0))
        if dest == src.move(-2, 0):
            self.setPiece(srcPiece, dest)
            self.removePiece(src)
            srcPiece.moveTo(dest)

            rookPos = src.move(-4, 0)
            rook: Rook = self.getPiece(rookPos)  # type: ignore
            self.setPiece(rook, src.move(-1, 0))
            self.removePiece(rookPos)
            rook.moveTo(src.move(-1, 0))
        self.updateCheck(srcPiece.color)

    def checkPawnPromotion(self, srcPiece: "Piece", dest: "Pos"):
        if not isinstance(srcPiece, Pawn):
            return False
        if srcPiece.color == Color.BLACK and dest.Y == 7:
            return True
        if srcPiece.color == Color.WHITE and dest.Y == 0:
            return True
        return False

    def pawnPromotionMove(
        self, src: "Pos", dest: "Pos", getInput: "Callable[[str],str]"
    ) -> "tuple[bool,bool]":
        selection = None
        while True:
            inp = getInput(
                "Choose what to upgrade - ['r','k','b','q'] - or 'e' to discard move > "
            ).upper()
            if inp == "E":
                return False, False
            if inp in ["R", "K", "B", "Q"]:
                selection = inp
                break
        srcColor = self.getPiece(src).color  # type: ignore
        newPiece = CLASS_MAP[selection](dest.X, dest.Y, srcColor)
        self.killPiece(dest)
        self.setPiece(newPiece, dest)
        self.removePiece(src)
        self.updateCheck(srcColor)
        if len(self.getAllPossibleMoves(srcColor.GetOpp())) == 0:
            return True, True
        return True, False

    def overrideMove(self, src: "Pos", dest: "Pos"):
        srcPiece = self.getPiece(src)
        if srcPiece == None:
            return
        self.killPiece(dest)
        self.setPiece(srcPiece, dest)
        self.removePiece(src)
        srcPiece.moveTo(dest)
        self.updateCheck(srcPiece.color)

    def killPiece(self, pos: "Pos"):
        piece = self.getPiece(pos)
        if piece != None:
            self.deaths.append(piece)
        self.setPiece(None, pos)

    def getPiece(self, pos: "Pos") -> "Piece|None":
        if not self.isValidPos(pos):
            return None
        return self.board[pos.Y][pos.X]

    def createPiece(self, Piec: "type[Piece]", color: "Color", i, j) -> None:
        piece = Piec(i, j, color)
        self.board[j][i] = piece
        pass

    def setPiece(self, piece: "Piece|None", pos: "Pos"):
        if not self.isValidPos(pos):
            return
        self.board[pos.Y][pos.X] = piece

    def removePiece(self, pos: "Pos"):
        if not self.isValidPos(pos):
            return
        self.board[pos.Y][pos.X] = None

    def __repr__(self) -> str:
        repr = ""

        repr += "    " + "    ".join(["a", "b", "c", "d", "e", "f", "g", "h"]) + "   \n"

        repr += "  " + "╔" + "═" * 39 + "╗\n"
        repr += ("\n  ║" + "─" * 39 + "║\n").join(
            [
                (
                    str(8 - i)
                    + " "
                    + "║ "
                    + "  | ".join(
                        [str(UP.get(self.getPosRep(i, j), " ")) for j in range(8)]
                    )
                    + "  ║"
                )
                for i in range(8)
            ]
        )
        repr += "\n  ╚" + "═" * 39 + "╝"
        return repr

    def getPosRep(self, i, j):
        if self.board[i][j] == None:
            return "  "
        return str(self.board[i][j])

    # for pieces classes
    def isValidPos(self, pos: "Pos") -> bool:  # type: ignore
        return not (pos.X < 0 or pos.X > 7 or pos.Y < 0 or pos.Y > 7)

    def canMove(self, pos: "Pos") -> bool:
        if not self.isValidPos(pos):
            return False
        piece = self.getPiece(pos)
        if piece == None:
            return True
        return False

    def canKill(self, pos: "Pos", color: "Color") -> bool:
        if not self.isValidPos(pos):
            return False
        piece = self.getPiece(pos)
        if piece == None:
            return False
        if piece.color != color:
            return True
        return False

    def getDirection(self, color: "Color"):
        if color == Color.BLACK:
            return 1
        return -1

    def getKings(self) -> "tuple[King, King]":
        blackKing = None
        whiteKing = None
        for row in self.board:
            for piece in row:
                if piece == None:
                    continue
                if not isinstance(piece, King):
                    continue
                if piece.color == Color.BLACK:
                    blackKing = piece
                if piece.color == Color.WHITE:
                    whiteKing = piece
        return blackKing, whiteKing  # type: ignore

    def updateCheck(self, lastMove: "Color"):
        # find kings
        blackKing, whiteKing = self.getKings()
        if blackKing == None or whiteKing == None:
            self.checked = None
            return
        selfKing = blackKing if lastMove == Color.BLACK else whiteKing
        oppKing = whiteKing if lastMove == Color.BLACK else blackKing

        # check if self getting into check
        for row in self.board:
            for piece in row:
                if piece == None or piece.color == lastMove:
                    continue
                legalMoves, _ = piece.possibleMoves(self, depth=0)
                if selfKing.pos in legalMoves:
                    self.checked = selfKing.color
                    return

        # check if opp getting into check
        for row in self.board:
            for piece in row:
                if piece == None or piece.color != lastMove:
                    continue
                legalMoves, _ = piece.possibleMoves(self, depth=0)
                if oppKing.pos in legalMoves:
                    self.checked = oppKing.color
                    return
        self.checked = None

    def getPlayerPieces(self, color: "Color") -> "list[Piece]":
        pieces: "list[Piece]" = []
        for row in self.board:
            for piece in row:
                if piece != None and piece.color == color:
                    pieces.append(piece)
        return pieces

    def getAllPossibleMoves(self, color: "Color") -> "list[PossibleMoves]":
        pieces = self.getPlayerPieces(color)
        possibleMoves: "list[PossibleMoves]" = []
        for piece in pieces:
            legalMoves, _ = piece.possibleMoves(self)
            if len(legalMoves) > 0:
                possibleMoves.append(PossibleMoves(piece, legalMoves))
        return possibleMoves
