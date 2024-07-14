import React, { useEffect } from 'react';
import socketIOClient from "socket.io-client";
const ENDPOINT = "http://127.0.0.1:3000";

function App() {
  useEffect(() => {
    const socket = socketIOClient(ENDPOINT);
    socket.on("connect", () => {
      console.log(`Connected to server with id ${socket.id}`);
    });
  }, []);

  return (
    <div className="App">
      <h1>Hello from React!</h1>
    </div>
  );
}

export default App;
