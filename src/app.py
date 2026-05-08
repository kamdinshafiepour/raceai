import streamlit as st
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from data import get_fastest_laps, get_driver_standings

load_dotenv()

client = Anthropic()

tools = [
    {
        "name": "get_fastest_laps",
        "description": "Get the fastest lap times for a specific race and year. Use this when the user asks about lap times, fastest laps, or race performance at a specific event.",
        "input_schema": {
            "type": "object",
            "properties": {
                "race": {"type": "string", "description": "The race name e.g. Monaco, Silverstone, Monza"},
                "year": {"type": "integer", "description": "The year of the race e.g. 2023"}
            },
            "required": ["race", "year"]
        }
    },
    {
        "name": "get_driver_standings",
        "description": "Get the driver championship standings for a given year.",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "The championship year e.g. 2023"}
            },
            "required": ["year"]
        }
    }
]


def run_agent(user_message: str, conversation_history: list) -> str:
    conversation_history.append({"role": "user", "content": user_message})

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system="You are RaceAI, a motorsport data analyst. Use the available tools to fetch real data before answering. If a tool returns an error, tell the user clearly.",
            tools=tools,
            messages=conversation_history
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    with st.spinner(f"Fetching {block.name}..."):
                        if block.name == "get_fastest_laps":
                            result = get_fastest_laps(**block.input)
                        elif block.name == "get_driver_standings":
                            result = get_driver_standings(**block.input)
                        else:
                            result = {"error": "Unknown tool"}

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })

            conversation_history.append({"role": "assistant", "content": response.content})
            conversation_history.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            final_answer = response.content[0].text
            conversation_history.append({"role": "assistant", "content": final_answer})
            return final_answer


# --- Streamlit UI ---

st.set_page_config(page_title="RaceAI", page_icon="🏎️")
st.title("RaceAI")
st.caption("Formula 1 data analyst · powered by Claude + FastF1")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about any F1 race..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer = run_agent(prompt, st.session_state.conversation_history)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})