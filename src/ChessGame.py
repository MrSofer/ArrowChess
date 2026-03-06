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

class SelectHandler(BaseModel):
    index : int

class MoveHandler(BaseModel):
    moving_piece : int
    moving_to : int

pieces_translation = {

    "":0,
    "P":1,
    "p":-1,
    "N":2,
    "n":-2,
    "B":3,
    "b":-3,
    "R":4,
    "r":-4,
    "Q":5,
    "q":-5,
    "K":6,
    "k":-6
}

numbers_translation = {
    0:"",
    1:"P",
    -1:"p",
    2:"N",
    -2:"n",
    3:"B",
    -3:"b",
    4:"R",
    -4:"r",
    5:"Q",
    -5:"q",
    6:"K",
    -6:"k"
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

def coord_to_ind(i: int, j: int) -> int:
    return 8*i + j

def ind_to_coord(ind: int) -> tuple[int,int]:
    return ind // 8 , ind % 8


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
        self.en_passant = None

    def find_legal_moves(self,ind) -> list[int]: #todo: add checks, en passant, castling,promotion
        ret = list()
        piece_type = self.board[ind]
        i,j = ind_to_coord(ind)
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
                    step_one = coord_to_ind(i+color_sign,j)
                    if self.board[step_one] == 0:
                        ret.append(step_one)
                        step_two = coord_to_ind(i+2*color_sign,j)
                        if (i == 1 + (5 * self.turn)) and (self.board[step_two] == 0):
                            ret.append(step_two)
                    if j > 0:
                        take_left = step_one - 1
                        if color_sign * self.board[take_left] < 0 or take_left == self.en_passant:
                            ret.append(take_left)
                    if j < 7:
                        take_right = step_one + 1
                        if color_sign * self.board[take_right] < 0 or take_right == self.en_passant:
                            ret.append(take_right)
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
                        curr_ind = coord_to_ind(m, n)
                        print(curr_ind)
                        if self.board[curr_ind] == 0:
                            ret.append(curr_ind)
                        else:
                            if color_sign * self.board[curr_ind] < 0:
                                ret.append(curr_ind)
                            break
                        m += k
                        n += l

            elif len(moves) > 0:
                for k, l in moves:
                    curr_ind = coord_to_ind(i+k,j+l)
                    if (0 <= i + k <= 7) and (0 <= j + l <= 7) and (color_sign * self.board[curr_ind] <= 0):
                        ret.append(curr_ind)
        return ret

    def move(self,piece:int,towards:int) -> str:
        color_sign = 1 - 2*self.turn
        captures = self.board[towards] != ""
        self.board[towards] = self.board[piece]
        self.board[piece] = 0
        if self.en_passant == towards:
            self.board[towards - 8*color_sign] = 0
            captures = True
        if abs(self.board[towards]) == 1 and towards // 8 == 3 + self.turn:
            self.en_passant = towards - 8*color_sign
        else:
            self.en_passant = None
        self.turn = 1 - self.turn
        return str.upper(numbers_translation[self.board[towards]]) + ("x" if captures else "") + chr(97 + towards // 8) + str(towards % 8)

game : ChessGame = ChessGame()

@app.get("/reset")
async def resetGame():
    global game
    game = ChessGame()

@app.post("/get_moves")
async def calculate_moves(request:SelectHandler) -> dict:
    index = request.index
    calculated_list = game.find_legal_moves(index)
    return {"moves":calculated_list}

@app.post("/move")
async def move(request:MoveHandler) -> dict:
    moving_piece = request.moving_piece
    moving_to = request.moving_to
    move_name = game.move(moving_piece,moving_to)
    updated_board = [numbers_translation[game.board[i]] for i in range(len(game.board))]
    return {"move_name":move_name, "updated_board":updated_board}

"""
todo:
implement en passant
implement pins
implement castling
implement checks
make sure board is aligned with front
make sure board refreshes when page refreshes 
"""