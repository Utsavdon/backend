from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active rooms (max 2 users per room)
active_rooms = {}

@app.websocket("/ws/{room_id}/{user_name}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_name: str):
    """WebSocket signaling for video calls"""
    await websocket.accept()

    if room_id not in active_rooms:
        active_rooms[room_id] = []

    if len(active_rooms[room_id]) >= 2:
        await websocket.send_text(json.dumps({"error": "Room is full"}))
        await websocket.close()
        return

    active_rooms[room_id].append({"websocket": websocket, "name": user_name})

    # Notify users
    for participant in active_rooms[room_id]:
        await participant["websocket"].send_text(json.dumps({
            "action": "user_joined",
            "users": [p["name"] for p in active_rooms[room_id]]
        }))

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Forward messages to other users in the room
            for participant in active_rooms[room_id]:
                if participant["websocket"] != websocket:
                    await participant["websocket"].send_text(json.dumps(message))

    except WebSocketDisconnect:
        active_rooms[room_id] = [p for p in active_rooms[room_id] if p["websocket"] != websocket]
        if not active_rooms[room_id]:
            del active_rooms[room_id]
