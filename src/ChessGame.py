import fastapi, uvicorn
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestHandler(BaseModel):
    board : list[str]
    index : int


pieces_translation = {

    "":0,
    "p":1,
    "P":-1,
    "n":2,
    "N":-2,
    "b":3,
    "B":-3,
    "r":4,
    "R":-4,
    "q":5,
    "Q":-5,
    "k":6,
    "K":-6
}

numbers_translation = {
    0:"",
    1:"p",
    -1:"P",
    2:"n",
    -2:"N",
    3:"b",
    -3:"B",
    4:"r",
    -4:"R",
    5:"q",
    -5:"Q",
    6:"k",
    -6:"K"
}

class Check:
    def __init__(self ,attacker , attackerPos ,kingPos):
        self.attacker = attacker
        self.attackerPos = attackerPos
        self.kingPos = kingPos

    """def find_available_squares(self) -> list():
        ret = self.attackerPos()
        match abs(self.attacker):
            case 3:
            
            case 4:

            case 5:
            
        return ret"""


class ChessGame:
    def __init__(self):
        self.board = [4,2,3,5,6,3,2,4,
                      1,1,1,1,1,1,1,1,
                      0,0,0,0,0,0,0,0,
                      0,0,0,0,0,0,0,0,
                      0,0,0,0,0,0,0,0,
                      0,0,0,0,0,0,0,0,
                      -1,-1,-1,-1,-1,-1,-1,-1,
                      -4,-2,-3,-5,-6,-3,-2,-4]
        self.turn = 0 #0 is white's turn, 1 is black's turn
        self.is_in_check = False
        self.can_castle = [[True,True],[True,True]]
        self.pinned_pieces = set()

    def find_legal_moves(self,ind) -> list[int]: #todo: add checks, en passant, castling
        ret = list()
        piece_type = self.board[ind]
        i = ind // 8
        j = ind % 8
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
                    if self.board[ind + 8*color_sign] == 0:
                        ret.append(ind+8*color_sign)
                        if (i == 1 + (5 * self.turn)) and (self.board[ind + 16*color_sign] == 0):
                            ret.append(ind + 16*color_sign)
                    if (j > 0) and (((self.turn == 0) and (self.board[ind+8*color_sign - 1] < 0)) or ((self.turn == 1) and (self.board[ind+8*color_sign - 1] > 0))):
                        ret.append(ind+8*color_sign - 1)
                    if (j < 7) and (((self.turn == 0) and (self.board[ind+8*color_sign + 1] < 0)) or ((self.turn == 1) and (self.board[ind+8*color_sign + 1] > 0))):
                        ret.append(ind+8*color_sign + 1)
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
                        if self.board[8*m + n] == 0:
                            ret.append(8*m + n)
                        else:
                            if color_sign * self.board[8*m + n] < 0:
                                ret.append(8*m + n)
                            break
                        m += k
                        n += l

            elif len(moves) > 0:
                for k, l in moves:
                    if (0 <= i + k <= 7) and (0 <= j + l <= 7) and (color_sign * self.board[8*(i + k) + (j + l)] <= 0):
                        ret.append(8*(i + k) + (j + l))
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

game = ChessGame()

@app.post("/get_moves")
async def calculate_moves(request:RequestHandler):
    if request.index is None:
        return {"moves":[]}
    board = request.board
    index = request.index
    game.board = [pieces_translation[board[i]] for i in range(len(board))]
    calculated_list = game.find_legal_moves(index)
    return {"moves":calculated_list}