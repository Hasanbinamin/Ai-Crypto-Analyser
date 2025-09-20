# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from agent import agent  # import your agent

app = FastAPI(title="Market Sentiment Agent API")

class SentimentRequest(BaseModel):
    query: str  # e.g., "BTCUSDT 1 day"

class SentimentResponse(BaseModel):
    result: str

@app.post("/analyze", response_model=SentimentResponse)
async def analyze_market(req: SentimentRequest):
    # Run agent
    response = agent.invoke({"messages": [{"role": "user", "content": req.query}]})
    final_message = response["messages"][-1].content
    return {"result": final_message}
