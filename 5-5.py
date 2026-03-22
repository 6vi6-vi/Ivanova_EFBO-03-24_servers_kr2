from fastapi import FastAPI, Request, Header
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()


class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias = "User-Agent")
    accept_language: str = Field(..., alias = "Accept-Language")

    class Config:
        populate_by_name = True


@app.get("/headers")
async def get_headers(headers: Annotated[CommonHeaders, Header()]):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }


@app.get("/info")
async def get_info(request: Request, headers: Annotated[CommonHeaders, Header()]):
    response = {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }
    request.headers.get("X-Server-Time")
    return response