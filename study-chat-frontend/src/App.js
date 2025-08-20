import React, { useState } from 'react';

function App() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");

  const handleSend = async () => {
    const res = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input })
    });
    const data = await res.json();
    setResponse(data.reply);
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Study Guide Chatbot</h1>
      <input 
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask something..."
      />
      <button onClick={handleSend}>Send</button>
      <p>Bot: {response}</p>
    </div>
  );
}

export default App;
