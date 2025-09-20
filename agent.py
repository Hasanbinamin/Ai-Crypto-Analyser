import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from tool import get_taker_data
from tool import analyze_sentiment
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key
# Set up the API key
#genai.configure(api_key=GOOGLE_API_KEY)

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

def analyzer (symbol, days=0, hours=0, minutes=0, whale_threshold=100000):
    """
    Analyze market sentiment for a given trading pair.

    Args:
        symbol (str): Trading pair symbol, e.g., "BTCUSDT".
        days (int, optional): Number of days of data to include. Defaults to 0.
        hours (int, optional): Number of hours of data to include. Defaults to 0.
        minutes (int, optional): Number of minutes of data to include. Defaults to 0.
        whale_threshold (float, optional): Trade size threshold to classify as whale. Defaults to 100000.

    Returns:
        dict: Dictionary containing retail and whale sentiment indices and volumes.
    """
    buy_vol, sell_vol, whale_buy, whale_sell = get_taker_data(symbol, days, hours, minutes, whale_threshold)    
    results = analyze_sentiment(buy_vol, sell_vol, whale_buy, whale_sell)
    return results
    




agent = create_react_agent(
    model,
    tools=[analyzer],
    prompt='''You are a Market Sentiment AI Agent. 
Your role is to analyze market sentiment using the analyzer tool. 
Always ask the user for a trading pair (e.g., BTCUSDT) and an optional time window (days, hours, minutes). 
Then call the analyzer tool with those inputs.

When results are available, interpret them as follows:

1. Retail Sentiment Index (range: -1 to +1)
   - Positive values (>0) → bullish bias among retail traders
   - Negative values (<0) → bearish bias among retail traders
   - Values near zero (-0.05 to +0.05) → retail sentiment is balanced

2. Whale Sentiment Index (range: -1 to +1)
   - Positive values (>0) → bullish bias among whales / large traders
   - Negative values (<0) → bearish bias among whales / large traders
   - Values near zero (-0.05 to +0.05) → whale sentiment is balanced

Apply Action Market Theory:

- If whales bullish and retail bearish → accumulation phase, potential upward move
- If both bullish → trend continuation upward
- If both bearish → trend continuation downward
- If both indices are near zero → market is balanced / indecisive
- If indices diverge → highlight divergence and explain implications

Format your response as:

1. Retail Sentiment → clear summary  
2. Whale Sentiment → clear summary  
3. Comparison → alignment or divergence  
4. Conclusion → Bullish / Bearish / Balanced  
5. Optional insight → one sentence, simple and human-readable''',

)

if __name__ == "__main__":
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "LTCUSDT 10 hours"}]}
    )

    final_massage = response["messages"][-1].content
    print(final_massage)