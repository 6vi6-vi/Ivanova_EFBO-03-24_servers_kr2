from fastapi import FastAPI, Response, Request, HTTPException, Form
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import uuid
import time

app = FastAPI()

SECRET_KEY = "your-secret-key-here"
serializer = URLSafeTimedSerializer(SECRET_KEY)

valid_users = {
    "user123": "password123"
}

SESSION_DURATION = 300
UPDATE_THRESHOLD = 180


def create_session_token(user_id: str, timestamp: int) -> str:
    data = f"{user_id}.{timestamp}"
    return serializer.dumps(data)


def parse_session_token(token: str):
    try:
        data = serializer.loads(token, max_age = SESSION_DURATION)
        user_id, timestamp = data.rsplit('.', 1)
        return user_id, int(timestamp)
    except (SignatureExpired, BadSignature, ValueError):
        return None, None


@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if username in valid_users and valid_users[username] == password:
        user_id = str(uuid.uuid4())
        timestamp = int(time.time())
        session_token = create_session_token(user_id, timestamp)
        response.set_cookie(
            key = "session_token",
            value = session_token,
            httponly = True,
            secure = False,
            max_age = SESSION_DURATION
        )
        return {"message": "Login successful"}
    raise HTTPException(status_code = 401, detail = "Invalid credentials")


@app.get("/profile")
async def get_profile(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if not session_token:
        response.status_code = 401
        return {"message": "Session expired"}

    user_id, timestamp = parse_session_token(session_token)
    if user_id is None:
        response.status_code = 401
        return {"message": "Invalid session"}

    current_time = int(time.time())
    time_passed = current_time - timestamp

    if time_passed > SESSION_DURATION:
        response.status_code = 401
        return {"message": "Session expired"}

    if time_passed >= UPDATE_THRESHOLD:
        new_timestamp = current_time
        new_session_token = create_session_token(user_id, new_timestamp)
        response.set_cookie(
            key = "session_token",
            value = new_session_token,
            httponly = True,
            secure = False,
            max_age = SESSION_DURATION
        )

    return {"user_id": user_id, "profile": "Profile information"}