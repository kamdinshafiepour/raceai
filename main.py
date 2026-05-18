from anthropic import Anthropic
from dotenv import load_dotenv
import json
from data import get_fastest_laps, get_driver_standings

load_dotenv()

client = Anthropic()

tools = [
    {
        "name": "get_fastest_laps",
        "description":"Get the fastest lap times for a specific race and year. Use this when the user asks about lap times, fastest laps, or race performance at a specific event.",
        "input_schema": {
            "type": "object",
            "properties": {
                "race": {
                    "type": "string",
                    "description": "The race name e.g. Monaco, Silverstone, Monza"
                },
                "year": {
                    "type": "integer",
                    "description": "The year of the race e.g. 2023"
                }
            },
            "required": ["race", "year"]
        }
    },
    {
        "name": "get_driver_standings",
        "description": "Get the driver championship standings for a given year. Use this when the user asks about points, standings, or who won the championship.",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {
                    "type": "integer",
                    "description": "The championship year e.g. 2023"
                }
            },
            "required": ["year"]
        }
    }
]

# --- the agent loop ---
def run_agent(user_message: str, conversation_history: list) -> str:
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system="You are RaceAI, a motorsport data analyst. Use the available tools to fetch real data before answering questions about races or standings. Always use a tool if one is relevant.",
            tools=tools,
            messages=conversation_history
        )

        # AI wants to call a tool
        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    print(f"\n[Calling {tool_name} with {tool_input}]")

                    if tool_name == "get_fastest_laps":
                        result = get_fastest_laps(**tool_input)
                    elif tool_name == "get_driver_standings":
                        result = get_driver_standings(**tool_input)
                    else:
                        result = {"error": "Uknown tool"}

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })
                
        
            conversation_history.append({
                "role": "assistant",
                "content": response.content
            })

            conversation_history.append({
                "role": "user",
                "content": tool_results
            })

        # AI has the final answer
        elif response.stop_reason == "end_turn":
            final_answer = response.content[0].text
            conversation_history.append({
                "role": "assistant",
                "content": final_answer
            })
            return final_answer

# --- main chat loop ---

conversation_history = []
print("RaceAI ready. Type 'quit' to exit.\n")

while True:
    user_input = input("You ").strip()
    if user_input.lower() == "quit":
        break
    if not user_input:
        continue

    answer = run_agent(user_input, conversation_history)
    print(f"\nRaceAI: {answer}\n")