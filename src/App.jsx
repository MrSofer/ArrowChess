import React, {useEffect, useState} from "react";
//import {useWindowDimensions} from "react-native";
import "./styles.css";

const initialBoard = [
    "R", "N", "B", "Q", "K", "B", "N", "R",
    "P", "P", "P", "P", "P", "P", "P", "P",
    "",  "",  "",  "",  "",  "",  "",  "",
    "",  "",  "",  "",  "",  "",  "",  "",
    "",  "",  "",  "",  "",  "",  "",  "",
    "",  "",  "",  "",  "",  "",  "",  "",
    "p", "p", "p", "p", "p", "p", "p", "p",
    "r", "n", "b", "q", "k", "b", "n", "r"
];

const BOARD_LENGTH = 64

function Square({color,value,isChosen , isLegalMove ,onSquareClick}){

    const boardColors = {
        light: "#FFE9CC",
        dark: "#A6845E"
    };

    const PIECES = {
        "P": "../images/white pawn.svg",
        "p": "../images/black pawn.svg",
        "N": "../images/white knight.svg",
        "n": "../images/black knight.svg",
        "B": "../images/white bishop.svg",
        "b": "../images/black bishop.svg",
        "R": "../images/white rook.svg",
        "r": "../images/black rook.svg",
        "Q": "../images/white queen.svg",
        "q": "../images/black queen.svg",
        "K": "../images/white king.svg",
        "k": "../images/black king.svg",
    };
    const isEmpty = value === "";


    return (
        <button style={{
                    height:"90px",
                    width:"90px",
                    borderRadius: 0,
                    backgroundColor:boardColors[color],
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    border: "none",
                    padding: 0,
                    position: "relative"
                }}
                className={`square ${isChosen ? "square-chosen" : "square-not-chosen"}`}
                onClick={onSquareClick}
        >

            {isLegalMove && (
                <img
                    src={isEmpty ? "../images/shadow_empty.png" : "/../images/shadow_take.png" }
                    alt="legal move"
                    style={{
                        position: "absolute",
                        width: isEmpty ? "50%" : "60%",
                        height: isEmpty ? "50%" : "60%",
                        zIndex: 1,
                        //opacity: 0.7,
                        pointerEvents: "none"
                    }}
                />
            )}

            {value &&
                (<img src={PIECES[value]}
                      alt={value}
                      style={{
                        position: "relative",
                        width:"80%",
                        height:"80%",
                        backgroundSize: "600% 200%",
                        imageRendering: "smooth",
                        objectFit: "contain",
                        zIndex: 2,
                        pointerEvents: "none"
                      }}
                />)
            }
        </button>
    )
}

function Board({turn,squares,onBoardClick,legalMoves,selectedSquare}){


    return (
        <div className="parent-container">
            <div className={"chess-board"}>
                {squares.map((piece , index) => {
                    const row = Math.floor(index / 8);
                    const col = index % 8;
                    const isDark = (row+col) % 2 === 0;
                    const isLegal = legalMoves.includes(index);

                    return(
                        <Square
                            key={index}
                            value={piece}
                            color={isDark ? "dark" : "light"}
                            isChosen={selectedSquare === index && piece !== ""} /*todo: can't choose a piece which is not yours*/
                            isLegalMove={isLegal}
                            onSquareClick={() => {onBoardClick(index)}}
                        />
                    );
                })}
            </div>
        </div>
    )
}

export default function App() {
    const [squares, setSquares] = useState(initialBoard)
    const [selectedSquare, setSelectedSquare] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);

    const requestOptions = {
        method:"POST",
        headers:{"Content-Type": "application/json"}
    }

    useEffect(()=>{
        try{
            fetch("http://localhost:8000/reset");
        }
        catch{
            console.log("error - board reset");
        }

    },[])
    async function handleBoardClick(i){
        let requestBody, response, json;
        if (legalMoves.includes(i)){

            try {

            requestBody = JSON.stringify({
                moving_piece:selectedSquare,
                moving_to:i
                    });

            requestOptions["body"] = requestBody;

            response = await fetch("http://localhost:8000/move",requestOptions);
            json = await response.json();
            }
            catch {
                return;
            }
            const updatedBoard = json["updated_board"]
            setSquares(updatedBoard)
            setLegalMoves([]);
            setSelectedSquare(null);
            return;
        }
        if (i === selectedSquare) {setSelectedSquare(null); setLegalMoves([]); return;} // deselect a piece
        setSelectedSquare(i);
        try{
            requestBody = JSON.stringify({index:i});
            requestOptions["body"] = requestBody
            response = await fetch("http://localhost:8000/get_moves",requestOptions);
            json = await response.json();
            setLegalMoves(json.moves);
        }
        catch{
            setSelectedSquare(null);
            setLegalMoves([]);
        }
    }

    return (
        <Board
            squares={squares}
            selectedSquare={selectedSquare}
            legalMoves={legalMoves}
            onBoardClick={(index) => handleBoardClick(index)}
        />

    )
}
