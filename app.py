# app.py
from flask import Flask, request, jsonify, render_template
from datetime import datetime
import pandas as pd
from core.config import FEEDBACK_CSV, HOST, PORT, DEBUG
from agents.planner import planner_agent, build_context
from agents.optimizer import optimizer_agent
import json

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/plan", methods=["POST"])
def plan_route():
    data = request.get_json()
    # Simple validation
    required = ["crop","yield_t_per_ha","residue_tonnes","soil","location"]
    if not data or not all(k in data for k in required):
        return jsonify({"error":"Missing required fields. Provide crop, yield_t_per_ha, residue_tonnes, soil, location"}), 400
    # Normalize keys expected by planner
    user_input = {
        "crop": data["crop"],
        "yield_t_per_ha": float(data["yield_t_per_ha"]),
        "residue_tonnes": float(data["residue_tonnes"]),
        "soil": data["soil"],
        "location": data["location"]
    }
    # Planner
    initial = planner_agent(user_input)
    # If planner returned plan in different format, wrap
    if "plan" not in initial:
        initial = {"plan": initial, "user_input": user_input}

    # Make sure planner output has user_input for optimizer
    initial["user_input"] = user_input

    # Optimizer
    final = optimizer_agent(initial)
    print(final)
    # Compose user-facing output - send full initial object (with plan, reasoning, confidence)
    initial_plan_data = {
        "plan": initial.get("plan", {}),
        "reasoning": initial.get("reasoning", "No reasoning provided"),
        "confidence": initial.get("confidence", 0)
    }
    output = {
        "Input": user_input,
        "Initial_Plan": initial_plan_data,
        "Final_Output": final
    }
    return jsonify(output)

@app.route("/feedback", methods=["POST"])
def feedback_route():
    data = request.get_json() or {}
    rating = data.get("rating")
    comments = data.get("comments", "")
    user_input = data.get("user_input")
    output = data.get("output")
    if rating is None or user_input is None or output is None:
        return jsonify({"error": "Missing rating, user_input, or output"}), 400
    row = {
        "timestamp": datetime.utcnow().isoformat(timespec='seconds') + "Z",
        "rating": rating,
        "comments": comments,
        "user_input": json.dumps(user_input),
        "output": json.dumps(output)
    }
    try:
        df = pd.DataFrame([row])
        if FEEDBACK_CSV.exists():
            df.to_csv(FEEDBACK_CSV, mode='a', header=False, index=False)
        else:
            df.to_csv(FEEDBACK_CSV, index=False)
    except Exception as e:
        return jsonify({"error": f"Failed to save feedback: {e}"}), 500
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
