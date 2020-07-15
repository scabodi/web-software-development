"use strict";
var myGamePiece;
var enemyPiece;

var myGameArea = {
    canvas : document.createElement("canvas"),
    start : function () {
        this.canvas.width = 480;
        this.canvas.height = 270;
        this.context = this.canvas.getContext("2d");
        document.body.insertBefore(this.canvas, document.body.childNodes[0]);
        this.interval = setInterval(updateGameArea, 15);        
    },
    stop : function () {
        clearInterval(this.interval);
    },    
    clear : function () {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}

function component(width, height, color, x, y, type) {
    this.type = type;
    this.width = width;
    this.height = height;
    this.x = x;
    this.y = y;    
    this.speed = 5; 
    this.score = 0;
    this.update = function() {
        var ctx = myGameArea.context;
        ctx.fillStyle = color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
    this.updateScore = function () {
        this.score += 0.02;
        document.getElementById("score").innerHTML = "<b>Score:</b> " + Math.round(this.score);

    }
}

function startGame() {
    myGamePiece = new component(30, 30, "green", 200, 200);
    enemyPiece = new component(30, 30, "red", 10, 10);
    setTimeout(function () {
        myGameArea.start();
    }, 500);
}

// Main game loop here
function updateGameArea() {
    if (endCondition()) {
        gameOver();
    }
    else {
        myGameArea.clear();
        myGamePiece.update();
        enemyPiece.update();
        myGamePiece.updateScore();
        chase();
    }
}

function gameOver() {
    myGameArea.stop();
    myGameArea.clear();
    myGameArea.context.font = "40px arial";
    myGameArea.context.fillStyle = "Black"
    myGameArea.context.fillText("Game Over!", myGameArea.canvas.width / 3.5, myGameArea.canvas.height / 1.8);
    sendScore();
}

function sendScore() {
    var msg = {
        "messageType": "SCORE",
        "score": myGamePiece.score
    };
    window.parent.postMessage(msg, "*");
}

function moveTo(x,y) {
    if (x > 0 && myGameArea.canvas.width > x + (myGamePiece.width))
        myGamePiece.x = x;
    if (y > 0 && myGameArea.canvas.height > y + (myGamePiece.height))
        myGamePiece.y = y
}

function chase() {
    if (myGamePiece.x > enemyPiece.x) {
        enemyPiece.x += 1;
    }
    else if (myGamePiece.y > enemyPiece.y) {
        enemyPiece.y += 1;
    }
    else if (myGamePiece.x < enemyPiece.x) {
        enemyPiece.x -= 1;
    }
    else if (myGamePiece.y < enemyPiece.y) {
        enemyPiece.y -= 1;
    }
}

function endCondition() {
    if ( myGamePiece.x < enemyPiece.x + enemyPiece.width &&
        myGamePiece.x + myGamePiece.width > enemyPiece.x &&
        myGamePiece.y < enemyPiece.y + enemyPiece.height &&
        myGamePiece.y + myGamePiece.height > enemyPiece.y){
        return true;
    }
    else
        return false;
}
function checkKey(e) {
    if (endCondition())
        return;
    e = e || window.event;

    if (e.keyCode == '38') {
        moveTo(myGamePiece.x, myGamePiece.y - myGamePiece.speed);
    }
    else if (e.keyCode == '40') {
        moveTo(myGamePiece.x, myGamePiece.y + myGamePiece.speed);
    }
    else if (e.keyCode == '37') {
        moveTo(myGamePiece.x - myGamePiece.speed, myGamePiece.y);
    }
    else if (e.keyCode == '39') {
        moveTo(myGamePiece.x + myGamePiece.speed, myGamePiece.y);
    }
}

function saveGame() {
    var msg = {
        "messageType": "SAVE",
        "gameState": {
            "player_x" : myGamePiece.x,
            "player_y" :  myGamePiece.y,
            "enemy_x" : enemyPiece.x,
            "enemy_y" : enemyPiece.y,
            "score": myGamePiece.score
        }
    };
    window.parent.postMessage(msg, "*");
}

function loadGame() {
    var msg = {
        "messageType": "LOAD_REQUEST",
    };
    window.parent.postMessage(msg, "*");
}


function newGame() {
    myGameArea.stop();
    myGameArea.clear();
    startGame();
}

function initGame() {
    setTimeout(function() {
        var message =  {
            messageType: "SETTING",
            options: {
                "width": 550, //Integer
                "height": 450 //Integer
            }
        };
        window.parent.postMessage(message, "*");

        startGame();
        document.getElementById("loadtext").innerHTML = "";
    }, 2000);
}


// event listeners
window.addEventListener("message", function(evt) {
    if(evt.data.messageType === "LOAD") {
        newGame();
        setTimeout(function() {
            myGamePiece.x = evt.data.gameState.player_x;
            myGamePiece.y = evt.data.gameState.player_y;
            enemyPiece.x = evt.data.gameState.enemy_x;
            enemyPiece.y = evt.data.gameState.enemy_y;
            myGamePiece.score = evt.data.gameState.score
        }, 100);
    } else if (evt.data.messageType === "ERROR") {
        alert(evt.data.info);
    }
});


window.onload = initGame;
document.onkeydown = checkKey; //arrowkeys