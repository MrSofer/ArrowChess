import React, {useState} from "react";
//import {useWindowDimensions} from "react-native";
import "./styles.css";

const initialBoard = [
    "r", "n", "b", "q", "k", "b", "n", "r",
    "p", "p", "p", "p", "p", "p", "p", "p",
    "",  "",  "",  "",  "",  "",  "",  "",
    "",  "",  "",  "",  "",  "",  "",  "",
    "",  "",  "",  "",  "",  "",  "",  "",
    "",  "",  "",  "",  "",  "",  "",  "",
    "P", "P", "P", "P", "P", "P", "P", "P",
    "R", "N", "B", "Q", "K", "B", "N", "R"
];

function Square({color,value,isChosen , isLegalMove ,onSquareClick}){

    const boardColors = {
        light: "#FFE9CC",
        dark: "#A6845E"
    };

    const PIECES = {
        "p": "../images/white pawn.svg",
        "P": "../images/black pawn.svg",
        "n": "../images/white knight.svg",
        "N": "../images/black knight.svg",
        "b": "../images/white bishop.svg",
        "B": "../images/black bishop.svg",
        "r": "../images/white rook.svg",
        "R": "../images/black rook.svg",
        "q": "../images/white queen.svg",
        "Q": "../images/black queen.svg",
        "k": "../images/white king.svg",
        "K": "../images/black king.svg",
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
                    const turn = 0;

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

    async function handleBoardClick(i){
        if (i === selectedSquare) {setSelectedSquare(null); setLegalMoves([]); return;} // deselect a piece
        setSelectedSquare(i);
        try{
            const requestBody = JSON.stringify({board:squares,index:i});
            const requestOptions = {
                method:"POST",
                headers:{"Content-Type": "application/json"},
                body:requestBody
            }
            const response = await fetch("http://localhost:8000/get_moves",requestOptions);
            const json = await response.json();
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
            onBoardClick={(i) => handleBoardClick(i)}
        />

    )
}
