# RaceAI 🏎️

A conversational Formula 1 data analyst built with Claude AI and FastF1.
Ask natural language questions about race lap times and championship standings -
the AI fetches real data and answers intelligently.

## Live demo

👉 [raceai-ks-pr1.streamlit.app](https://raceai-ks-pr1.streamlit.app/)

## Example questions

- What were the fastest laps at Monaco 2023?
- Who won the 2024 championship?
- What were the fastest laps at Silverstone 2022?
- Who led the 2021 championship?

## What it does

- Fastest lap times for any F1 race and year
- Driver championship standings with full season points
- Multi-turn conversation with full context memory
- Real F1 data from two dedicated sources

## Tech stack

- Python
- Anthropic Claude API (AI + tool use)
- FastF1 (official F1 telemetry — lap times)
- Ergast API via Jolpi (championship standings)
- Streamlit (UI)

## How it works

The AI uses tool use to decide when to fetch real data.
When you ask a question, Claude reads the available tools,
calls the right one with the right arguments, receives the
real data back, and answers based on it.
This is the core pattern behind AI agents.

## Running locally

1. Clone the repo
2. Install dependencies
   ```
   pip install -r requirements.txt
   ```
3. Add your Anthropic API key to a `.env` file
   ```
   ANTHROPIC_API_KEY=your-key-here
   ```
4. Run the app
   ```
   streamlit run src/app.py
   ```

## Deploying to Streamlit Cloud

1. Fork this repo
2. Go to share.streamlit.io and connect your GitHub
3. Set main file path to `src/app.py`
4. Add your Anthropic API key in Settings → Secrets
   ```toml
   ANTHROPIC_API_KEY = "your-key-here"
   ```