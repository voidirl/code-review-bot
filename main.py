import hmac
import hashlib
import httpx
from fastapi import FastAPI,Request,HTTPException
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

GITHUB_TOKEN=os.getenv("GITHUB_TOKEN")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
WEBHOOK_SECRET=os.getenv("GITHUB_WEBHOOK_SECRET")

def verify_signature(payload: bytes,signature: str) -> bool:
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(), payload,hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected,signature)