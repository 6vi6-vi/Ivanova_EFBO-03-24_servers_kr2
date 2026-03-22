from fastapi import FastAPI, Response, Request, HTTPException, Form
from pydantic import BaseModel
import uuid

app = FastAPI()

valid_users = {
    "user123": "password123"
}

sessions = {}

class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if username in valid_users and valid_users[username] == password:
        session_token = str(uuid.uuid4())
        sessions[session_token] = username
        response.set_cookie(key = "session_token", value = session_token, httponly = True)
        return {"message": "Login successful"}
    raise HTTPException(status_code = 401, detail = "Invalid credentials")

@app.get("/user")
async def get_user(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token and session_token in sessions:
        username = sessions[session_token]
        return {"username": username, "profile": f"Profile info for {username}"}
    raise HTTPException(status_code = 401, detail = "Unauthorized")