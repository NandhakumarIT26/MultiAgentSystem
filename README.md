# Residue Utilization Planner (Starter)

## Overview
Lightweight prototype:
- CSV-based Knowledge Base
- Planner Agent (LLM-assisted)
- Optimizer Agent (LLM-assisted + rule-based checks)
- Flask API to submit input and get final optimized plan (JSON)

## Setup
1. Create a Python venv and activate:
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows

2. Install requirements:
   pip install -r requirements.txt

3. Put your LLM API key (optional) in `.env`:
   OPENAI_API_KEY=your_key_here

4. Run the Flask app:
   python app.py

5. Example API:
   POST http://127.0.0.1:5000/plan
   Body JSON:
   {
     "crop": "Rice",
     "yield_t_per_ha": 6.2,
     "residue_tonnes": 8.5,
     "soil": "Clay",
     "location": "Thanjavur, Tamil Nadu"
   }

## Notes
- The `llm_adapter` has two modes:
  - `use_llm = True` → calls configured LLM via OpenAI (replace with your provider)
  - `use_llm = False` → uses a deterministic fallback function for testing
