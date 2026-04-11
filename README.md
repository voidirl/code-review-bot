# Code Review Bot

An AI-powered GitHub PR code reviewer built with FastAPI and Groq (LLaMA 3.3-70b).

## How it works
1. Open or update a PR on a connected GitHub repo
2. GitHub sends a webhook to the bot
3. Bot fetches the PR diff and sends it to Groq for review
4. AI review is posted as a comment on the PR

## Stack
- FastAPI
- Groq API (LLaMA 3.3-70b)
- GitHub Webhooks
- Deployed on Railway

## Setup
1. Clone the repo
2. Create `.env` with:

 GITHUB_TOKEN=your_token\n
 GROQ_API_KEY=your_key\n
 GITHUB_WEBHOOK_SECRET=your_secret

3. Install deps: `pip install -r requirements.txt`
4. Run: `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Set webhook URL in your GitHub repo settings
