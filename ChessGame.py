class ChessGame:
    def __init__(self):
        self.board = [[4,2,3,5,6,3,2,4],
                      [1 for _ in range(8)],
                      [0 for _ in range(8)],
                      [0 for _ in range(8)],
                      [0 for _ in range(8)],
                      [0 for _ in range(8)],
                      [-1 for _ in range(8)],
                      [-4,-2,-3,-5,-6,-3,-2,-4]]
        self.turn = 0 #0 is white, 1 is black
        self.is_in_check = False
        self.can_castle = [[True,True],[True,True]]
        self.pinned_pieces = set()

    def find_legal_moves(self,i,j) -> set: #todo: add checks, en passant, castling
        ret = set()
        piece_type = self.board[i][j]
        directions = []
        moves = []
        color_sign = 1 - 2*self.turn
        if self.is_in_check:
            pass #todo after implementing checks
        else:
            if color_sign * piece_type <= 0:
                return ret
            match abs(piece_type):
                case 1:
                    if self.board[i+color_sign][j] == 0:
                        ret.add((i+color_sign,j))
                        if (i == 1 + (5 * self.turn)) and (self.board[4 + self.turn][j] == 0):
                            ret.add((4 + self.turn,j))
                    if (j > 0) and (((self.turn == 0) and (self.board[i+color_sign][j-1] < 0)) or ((self.turn == 1) and (self.board[i+color_sign][j-1] > 0))):
                        ret.add((i+color_sign,j-1))
                    if (j < 7) and (((self.turn == 0) and (self.board[i+color_sign][j+1] < 0)) or ((self.turn == 1) and (self.board[i+color_sign][j+1] > 0))):
                        ret.add((i+color_sign,j+1))
                case 2:
                    moves = [(-1,-2),(-1,2),(-2,-1),(-2,1),(1,-2),(1,2),(2,-1),(2,1)]
                case 3:
                    directions = [(-1,-1),(-1,1),(1,-1),(1,1)]
                case 4:
                    directions = [(-1, 0),(0, -1),(1, 0),(0, 1)]
                case 5:
                    directions = [(-1,-1),(-1,1),(1,-1),(1,1),(-1, 0),(0, -1),(1, 0),(0, 1)]
                case 6:
                    moves = [(-1,-1),(-1,1),(1,-1),(1,1),(-1, 0),(0, -1),(1, 0),(0, 1)]


            if len(directions) > 0:
                for k, l in directions:
                    m = i + k
                    n = j + l
                    while (0 <= m <= 7) and (0 <= n <= 7):
                        if self.board[m][n] == 0:
                            ret.add((m, n))
                        else:
                            if color_sign * self.board[m][n] < 0:
                                ret.add((m, n))
                            break
                        m += k
                        n += l

            elif len(moves) > 0:
                for k, l in moves:
                    if (0 <= i + k <= 7) and (0 <= j + l <= 7) and (color_sign * self.board[i + k][j + l] <= 0):
                        ret.add((i + k, j + l))
        return ret





"""    def move(self, mov):
        match mov[0]:
            case "N":

            case "B":

            case "R":

            case "Q":

            case "K":

            case "O":
                if len(mov) == 3:
                    if self.turn == "white":
                        self.board[0][7] = 6
                        self.board[0][6] = 4
                        self.board[0][]
            
            case _:"""
