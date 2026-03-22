from fastapi import FastAPI, Response, Request, HTTPException, Form
from itsdangerous import URLSafeTimedSerializer
import uuid

app = FastAPI()

SECRET_KEY = "your-secret-key-here"
serializer = URLSafeTimedSerializer(SECRET_KEY)

valid_users = {
    "user123": "password123"
}

@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if username in valid_users and valid_users[username] == password:
        user_id = str(uuid.uuid4())
        session_token = serializer.dumps(user_id)
        response.set_cookie(key = "session_token", value = session_token, httponly = True, max_age = 3600)
        return {"message": "Login successful"}
    raise HTTPException(status_code = 401, detail = "Invalid credentials")

@app.get("/profile")
async def get_profile(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code = 401, detail = "Unauthorized")
    try:
        user_id = serializer.loads(session_token, max_age = 3600)
        return {"user_id": user_id, "profile": "Profile information"}
    except:
        raise HTTPException(status_code = 401, detail = "Unauthorized")