import fastapi, uvicorn
from networkx.utils.rcm import pseudo_peripheral_node
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

white_turn = 1
black_turn = -1

empty_square = 0
pawn = white_pawn = 1
knight = white_knight = 2
bishop = white_bishop = 3
rook = white_rook = 4
queen = white_queen = 5
king = white_king = 6
black_pawn = -1
black_knight = -2
black_bishop = -3
black_rook = -4
black_queen = -5
black_king = -6

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

knight_moves = [(-1,-2),(-1,2),(-2,-1),(-2,1),(1,-2),(1,2),(2,-1),(2,1)]

bishop_directions = [(-1,-1),(-1,1),(1,-1),(1,1)]

rook_directions = [(-1, 0),(0, -1),(1, 0),(0, 1)]

queen_directions = king_moves = [(-1,-1),(-1,1),(1,-1),(1,1),(-1, 0),(0, -1),(1, 0),(0, 1)]

moves = [(knight, knight_moves), (king, king_moves)]
directions = [(bishop, bishop_directions), (rook,rook_directions)]

ROWS = COLS = 8
BOARD_LEN = 64


def coord_to_ind(row: int, col: int) -> int:
    return ROWS*row + col

def ind_to_coord(ind: int) -> tuple[int,int]:
    return ind // ROWS , ind % COLS


class ChessGame:

    board : list[int]
    turn : int
    is_check : bool
    kings : list[int]
    can_castle = list[list[bool]]


    def __init__(self):
        self.board = [white_rook,white_knight,white_bishop,white_queen,white_king,white_bishop,white_knight,white_rook,
                      white_pawn,white_pawn,white_pawn,white_pawn,white_pawn,white_pawn,white_pawn,white_pawn,
                      empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,
                      empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,
                      empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,
                      empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,empty_square,
                      black_pawn,black_pawn,black_pawn,black_pawn,black_pawn,black_pawn,black_pawn,black_pawn,
                      black_rook,black_knight,black_bishop,black_queen,black_king,black_bishop,black_knight,black_rook]
        self.turn = white_turn #1 is white's turn, -1 is black's turn
        self.is_check = False
        self.kings = [-1,4,60]
        self.can_castle = [[],[True,True],[True,True]]
        self.en_passant = None
        
    def is_king_safe(self,king_ind) -> bool:
        
        king_row,king_col = ind_to_coord(king_ind)

        pawn_take_from_left = coord_to_ind(king_row + self.turn, king_col-1)
        pawn_take_from_right = coord_to_ind(king_row + self.turn, king_col+1)
        if ((king_col > 0) and (-1 * self.turn * self.board[pawn_take_from_left] == pawn)) or ((king_col < COLS - 1) and (-1 * self.turn * self.board[pawn_take_from_right] == pawn)): #an opposite color pawn can take the king
            return False

        for piece,piece_moves in moves:
            for k,l in piece_moves:
                curr_ind = coord_to_ind(king_row + k, king_col + l)
                if (0 <= king_row + k < ROWS) and (0 <= king_col + l < COLS) and (-1 * self.turn * self.board[curr_ind] == piece): #an opposite color knight/king can take the king
                    return False

        for piece,piece_directions in directions: #queen shares sliding vectors with rook and bishop, so no need to add a queen loop
            for k,l in piece_directions:
                m = king_row + k
                n = king_col + l
                while (0 <= m < ROWS) and (0 <= n < COLS):
                    curr_ind = coord_to_ind(m, n)
                    if -1 * self.turn * self.board[curr_ind] in [piece,queen]: #an opposite color bishop/rook/queen can take the king
                        return False
                    elif self.board[curr_ind] != empty_square: #a non-threatening piece is blocking the way in that direction
                        break
                    m += k
                    n += l

        return True

    def pseudo_move(self, ind, towards) -> tuple[int,bool]:
        captured_piece = self.board[towards]
        self.board[towards] = self.board[ind]
        self.board[ind] = empty_square
        is_en_passant = False
        if  self.turn * self.board[towards] == pawn and self.en_passant == towards:
            self.board[towards - ROWS * self.turn] = empty_square
            captured_piece = - self.turn * pawn
            is_en_passant = True

        if self.turn * self.board[towards] == king:
            self.kings[self.turn] = towards

        return captured_piece,is_en_passant

    def unmove(self, current_ind, original_ind, piece_captured, was_en_passant):
        self.board[original_ind] = self.board[current_ind]
        if was_en_passant:
            self.board[current_ind] = empty_square
            self.board[current_ind - self.turn * ROWS] = piece_captured
        else:
            self.board[current_ind] = piece_captured

        if self.turn * self.board[original_ind] == king:
            self.kings[self.turn] = original_ind

    def king_safety_check(self,ind,towards,legal_moves_list) -> None: #using the fact that lists in python are mutable
        piece_captured,is_en_passant = self.pseudo_move(ind,towards)
        if self.is_king_safe(self.kings[self.turn]):
            legal_moves_list.append(towards)
        self.unmove(towards,ind,piece_captured,is_en_passant)


    def find_legal_moves(self,ind) -> list[int]: #todo: add castling, promotion
        ret = list()
        piece_type = self.turn * self.board[ind]
        piece_row,piece_col = ind_to_coord(ind)
        legal_directions = []
        legal_moves = []
        match piece_type:
            case 1: #pawn
                step_one = coord_to_ind(piece_row+self.turn,piece_col)
                if self.board[step_one] == empty_square:
                    self.king_safety_check(ind,step_one,ret)
                    step_two = coord_to_ind(piece_row+ 2*self.turn ,piece_col)
                    if (piece_row == 1 + (5 * int(self.turn == black_turn))) and (self.board[step_two] == empty_square):
                        self.king_safety_check(ind,step_two,ret)
                if piece_col > 0:
                    take_left = step_one - 1
                    if self.turn * self.board[take_left] < 0 or take_left == self.en_passant:
                        self.king_safety_check(ind,take_left,ret)
                if piece_col < COLS-1:
                    take_right = step_one + 1
                    if self.turn * self.board[take_right] < 0 or take_right == self.en_passant:
                        self.king_safety_check(ind,take_right,ret)
            case 2: #knight
                legal_moves = knight_moves
            case 3: #bishop
                legal_directions = bishop_directions
            case 4: #rook
                legal_directions = rook_directions
            case 5: #queen
                legal_directions = queen_directions
            case 6: #king
                legal_moves = king_moves


        if len(legal_directions) > 0:
            for k, l in legal_directions:
                m = piece_row + k
                n = piece_col + l
                while (0 <= m < ROWS) and (0 <= n < COLS):
                    curr_ind = coord_to_ind(m, n)
                    if self.board[curr_ind] == empty_square:
                        self.king_safety_check(ind,curr_ind,ret)
                    else:
                        if self.turn * self.board[curr_ind] < 0:
                            self.king_safety_check(ind,curr_ind,ret)
                        break
                    m += k
                    n += l

        elif len(legal_moves) > 0:
            for k, l in legal_moves:
                curr_ind = coord_to_ind(piece_row+k,piece_col+l)
                if (0 <= piece_row + k < ROWS) and (0 <= piece_col + l < COLS) and (self.turn * self.board[curr_ind] <= 0):
                    self.king_safety_check(ind,curr_ind,ret)

        return ret

    def move(self,piece:int,towards:int) -> str:
        captures = self.board[towards] != empty_square
        self.board[towards] = self.board[piece]
        self.board[piece] = empty_square
        if (self.turn * self.board[towards] == pawn) and (self.en_passant == towards):
            self.board[towards -  self.turn * ROWS] = empty_square
            captures = True
        if self.turn * self.board[towards] == pawn and towards // ROWS == 3 + int(self.turn == black_turn):
            self.en_passant = towards - ROWS * self.turn
        else:
            self.en_passant = None

        if self.turn * self.board[towards] == king:
            self.kings[self.turn] = towards

        self.turn = -1 * self.turn
        return str.upper(numbers_translation[self.board[towards]]) + ("x" if captures else "") + chr(97 + towards % COLS) + str((towards // ROWS) + 1)




game : ChessGame = ChessGame()

@app.get("/reset")
async def reset_game():
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
implement pins
implement castling
implement checks
implement promotion
"""