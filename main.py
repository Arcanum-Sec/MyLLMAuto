"""Main FastAPI application for the auto parts CTF."""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
import os
from typing import Dict, List, Optional, Any
import logging
# Comment out geolite2 import to avoid dependency issues
# import geoip2.database
# from geolite2 import geolite2
import socket
import re

from chains import AutoPartsChain, EMPLOYEE_DB
from parts_db import search_parts, get_part_details, PARTS_DB

# Create a global variable to store the API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Initialize the FastAPI app
app = FastAPI()

# CORS middleware configuration with more permissive settings for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # More permissive for development
    allow_credentials=False,  # Changed to False since we're using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize the auto parts chain with the API key
auto_parts_chain = AutoPartsChain(OPENAI_API_KEY)

class Message(BaseModel):
    content: str

class PartQuery(BaseModel):
    query: str
    include_sensitive: bool = False

class ApiKeyRequest(BaseModel):
    api_key: str

class FlagSubmissionRequest(BaseModel):
    flag: str

# Define the valid flags
VALID_FLAGS = [
    "realflag=prompt_injection_master_2025",
    "realflag={Sensitive_Data_Exfiltration_Champion}",
    "realflag=employee_data_breach_expert",
    "realflag={absolutely_have_seen_this_before}",
    "realflag={local_storage_ftw}"
    # Add any other flags here
]

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html") as f:
        content = f.read()
    response = HTMLResponse(content=content)
    # We don't need this header anymore since we have the localStorage flag
    return response

@app.post("/api/set_api_key")
async def set_api_key(request: ApiKeyRequest):
    """Set the OpenAI API key for the application."""
    global OPENAI_API_KEY
    
    # Validate the API key format (simple check)
    if not request.api_key.startswith("sk-") or len(request.api_key) < 20:
        raise HTTPException(status_code=400, detail="Invalid API key format")
    
    # Set the API key
    OPENAI_API_KEY = request.api_key
    
    return {"status": "success", "message": "API key set successfully"}

@app.post("/api/validate_flag")
async def validate_flag(request: FlagSubmissionRequest):
    """Validate a submitted flag."""
    # Check if the flag is valid
    if request.flag in VALID_FLAGS:
        return {
            "status": "success", 
            "valid": True, 
            "message": "Congratulations! You found a valid flag!"
        }
    else:
        return {
            "status": "error", 
            "valid": False, 
            "message": "Invalid flag. Keep searching!"
        }

@app.post("/api/chat")
async def chat(message: Message, request: Request) -> Dict[str, Any]:
    """Process a chat message through the LLM chains."""
    try:
        if not message.content.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
            
        client_ip = request.client.host
        response = auto_parts_chain.process_message(message.content, client_ip)
        if not response:
            raise HTTPException(status_code=404, detail="No results found")
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parts/search")
async def search_parts_api(query: PartQuery, request: Request) -> Dict[str, List[Dict[str, Any]]]:
    """Search for parts matching the query."""
    try:
        # First, process the query through the LLM chain (making it vulnerable to prompt injection)
        client_ip = request.client.host
        chain_response = auto_parts_chain.process_message(query.query, client_ip)
        
        # Then search for parts matching the query
        parts = search_parts(query.query)
        if not parts:
            return {"parts": []}
        
        # Convert to a list of parts with names
        parts_list = []
        for part_name, specs in parts.items():
            parts_list.append({
                "name": part_name.capitalize(),
                "category": specs.get("type", "Unknown"),
                "part_number": specs.get("part_number", "Unknown"),
                "specs": specs
            })
        
        return {"parts": parts_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/parts/{part_name}")
async def get_part_api(part_name: str) -> Dict[str, Any]:
    """Get detailed specifications for a part."""
    try:
        details = get_part_details(part_name)
        if not details:
            raise HTTPException(status_code=404, detail="Part not found")
        
        # Get engineering notes through the LLM chain
        engineering_response = None
        try:
            chain_response = auto_parts_chain.process_message(f"Tell me about {part_name}")
            engineering_response = chain_response.get("engineering_notes")
        except Exception:
            pass
        
        return {
            "name": part_name.capitalize(),
            "basic_specs": details,  
            "engineering_notes": engineering_response
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/internal/employee/{employee_id}")
async def get_employee_details(employee_id: str) -> Dict[str, Any]:
    """Vulnerable endpoint that exposes employee details through IDOR."""
    if employee_id in EMPLOYEE_DB:
        # Simulate a vulnerability by not checking authorization
        return EMPLOYEE_DB[employee_id]
    raise HTTPException(status_code=404, detail="Employee not found")

# Store connected websocket clients
connected_websockets = []

# Track which clients have already received the flag
clients_received_flag = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    client_id = id(websocket)
    connected_websockets.append(websocket)
    
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Remove the websocket when client disconnects
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)

async def send_flag_to_client(client_ip: str, websocket: WebSocket):
    """Send the flag to a client via websocket."""
    try:
        # Send a raw flag message that will be visible in Burp Suite but not processed by the frontend
        await websocket.send_text("CTF-FLAG-5: realflag={absolutely_have_seen_this_before}")
        # No longer tracking which clients have received the flag - send it every time
    except Exception as e:
        print(f"Error sending flag to client: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
