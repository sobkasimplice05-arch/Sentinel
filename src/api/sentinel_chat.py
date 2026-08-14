"""
💬 SENTINEL CHAT - Talk to Sentinel
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
from datetime import datetime
from loguru import logger
from src.core.simulated_internet import SimulatedInternet

app = FastAPI()
simulated_web = SimulatedInternet()

class SentinelChatbot:
    def __init__(self):
        self.web = simulated_web
        self.state = "exploring"
    
    async def process_message(self, message):
        logger.info(f"👤 User: {message}")
        
        if "search" in message.lower():
            return await self.web.search_vulnerability(message)
        elif "threats" in message.lower():
            return await self.web.fetch_threat_intelligence()
        elif "logs" in message.lower():
            return await self.web.generate_fake_logs()
        elif "status" in message.lower():
            return {"state": self.state, "message": "Exploring internet for threats"}
        else:
            return {"response": "Ask me to search threats, fetch intelligence, or check status"}

sentinel_bot = SentinelChatbot()

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("✅ Chat connected")
    
    try:
        while True:
            data = await websocket.receive_text()
            user_msg = json.loads(data)
            response = await sentinel_bot.process_message(user_msg["message"])
            
            await websocket.send_json({
                "timestamp": datetime.now().isoformat(),
                "from": "sentinel",
                "response": response
            })
    except WebSocketDisconnect:
        logger.info("❌ Chat disconnected")

@app.get("/chat")
async def get_chat():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>💬 Chat with Sentinel</title>
        <style>
            body { font-family: Arial; margin: 20px; background: #1a1a1a; color: #fff; }
            .container { max-width: 800px; margin: 0 auto; }
            #chat { border: 1px solid #444; height: 500px; overflow-y: auto; padding: 10px; background: #0a0a0a; margin: 20px 0; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background: #1e3a8a; text-align: right; }
            .sentinel { background: #7c2d12; }
            input { width: calc(100% - 22px); padding: 10px; margin-top: 10px; }
            button { padding: 10px 20px; cursor: pointer; background: #f97316; color: white; border: none; width: 100%; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Chat with Sentinel</h1>
            <p>Try: "search vulnerabilities", "fetch threats", "show logs", "status"</p>
            <div id="chat"></div>
            <input type="text" id="input" placeholder="Ask Sentinel...">
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws/chat");
            
            ws.onmessage = function(event) {
                const msg = JSON.parse(event.data);
                const chat = document.getElementById("chat");
                const div = document.createElement("div");
                div.className = "message sentinel";
                div.innerHTML = "<b>🤖 Sentinel:</b> " + JSON.stringify(msg.response, null, 2);
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            };
            
            function sendMessage() {
                const input = document.getElementById("input");
                const message = input.value;
                if(!message) return;
                
                const chat = document.getElementById("chat");
                const div = document.createElement("div");
                div.className = "message user";
                div.innerHTML = "<b>You:</b> " + message;
                chat.appendChild(div);
                
                ws.send(JSON.stringify({message: message}));
                input.value = "";
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

