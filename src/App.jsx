import React, {useState} from "react";
//import {useWindowDimensions} from "react-native";
import "./styles.css";

const initialBoard = [
    'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R',
    'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
    '',  '',  '',  '',  '',  '',  '',  '',
    '',  '',  '',  '',  '',  '',  '',  '',
    '',  '',  '',  '',  '',  '',  '',  '',
    '',  '',  '',  '',  '',  '',  '',  '',
    'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
    'r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'
];

function Square({color,value,isChosen,onSquareClick}){

    const colors = {
        light: "#FFE9CC",
        dark: "#A6845E"
    };

    const PIECES = {
        "p": "../pieces/white pawn.svg",
        "P": "../pieces/black pawn.svg",
        "n": "../pieces/white knight.svg",
        "N": "../pieces/black knight.svg",
        "b": "../pieces/white bishop.svg",
        "B": "../pieces/black bishop.svg",
        "r": "../pieces/white rook.svg",
        "R": "../pieces/black rook.svg",
        "q": "../pieces/white queen.svg",
        "Q": "../pieces/black queen.svg",
        "k": "../pieces/white king.svg",
        "K": "../pieces/black king.svg",
    };




    return (
        <button style={{
                    height:"90px",
                    width:"90px",
                    borderRadius: 0,
                    backgroundColor:colors[color],
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    border: "none",
                    padding: 0}}
                className={`square ${isChosen ? "square-chosen" : "square-not-chosen"}`}
                onClick={onSquareClick}
        >
            {value &&
                (<img src={PIECES[value]} alt={value} style={{
                    width:"80%",
                    height:"80%",
                    backgroundSize: "600% 200%",
                    imageRendering: "smooth",
                    objectFit: "contain",
                    pointerEvents: "none"
                }}></img>)}
        </button>
    )
}

function Board({turn,squares,onBoardClick,selectedSquare}){


    return (
        <div className="parent-container">
            <div className={"chess-board"}>
                {squares.map((piece , index) => {
                    const row = Math.floor(index / 8);
                    const col = index % 8;
                    const isDark = (row+col) % 2 == 1;

                    return(
                        <Square
                            key={index}
                            value={piece}
                            color={isDark ? "dark" : "light"}
                            isChosen={selectedSquare === index}
                            onSquareClick={() => {selectedSquare === index ? onBoardClick(null) : onBoardClick(index)}}
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

    return (
        <Board
            squares={squares}
            selectedSquare={selectedSquare}
            onBoardClick={(i) => setSelectedSquare(i)}
        />

    )
}
