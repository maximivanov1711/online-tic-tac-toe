const client_id = Math.floor(Math.random() * Math.pow(10, 10))
console.log(`You are User ${client_id}`);

const ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);

function cellClick(cellId) {
    ws.send(`Cell ${cellId} was clicked`);
}

ws.onmessage = function(e) {
    console.log(e);
}
