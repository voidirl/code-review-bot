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

@app.post("/webhook")
async def webhook(request: Request):
    payload_bytes = await request.body()
    signature = request.headers.get("X-Hub-Signature-256","")

    if not verify_signature(payload_bytes,signature):
        raise HTTPException(status_code=401,detail="Invalid signature")
    
    payload = await request.json()

    if payload.get("action") not in  ["opened","synchronize"]:
        return{"status": "ignored"}
    
    pr = payload["pull_request"]
    repo_full_name = payload["repository"]["full_name"]
    pr_number = pr["number"]
    diff_url = pr["diff_url"]

    async with httpx.AsyncClient() as client:
        diff_response = await client.get(
            diff_url,
            headers={"Authorization": f"token {GITHUB_TOKEN}"}
        )
        diff = diff_response.text

    async with httpx.AsyncClient() as client:
            groq_response = await client.post(
                 "https://api.groq.com/openai/v1/chat/completions",
                 headers={
                      "Authorization":f"Bearer {GROQ_API_KEY}",
                      "Content-Type": "appication/json"
                 },
                 json={
                      "model":"llama-3.3-70b-versatile",
                      "message": [
                           {
                                "role": "system",
                                "content": "You are an expert code reviewer. Give concise feedback on code quality, bugs, and improvements."
                           },
                           {
                                "role": "user",
                                "content": f"Review this PR diff:\n\n{diff[:8000]}"
                           }
                      ]
                 }
            )
            review = groq_response.json()["choices"][0]["message"]["content"]

            async with httpx.AsyncClient() as client:
                 await client.post( 
                      f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments",
                      headers={
                           "Authorization": "f"token{GITHUB_TOKEN}",
                           "Accept": "application/vnd.github.v3+json"
                        },
                      json={"body": f"**AI Code Review**\n\n{review}"}
                    )
                 return{"status": "review posted"}