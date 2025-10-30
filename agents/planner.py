# planner.py
import json
from core.llm_adapter import llm_call_system
from core.kb_loader import load_crop_data, load_soil_data, load_regional_data, load_policy_data

def build_context(user_input):
    # user_input is dict with keys crop, yield_t_per_ha, residue_tonnes, soil, location
    crop_df = load_crop_data()
    soil_df = load_soil_data()
    region_df = load_regional_data()
    policy_df = load_policy_data()

    crop = user_input.get("crop")
    soil = user_input.get("soil")
    location = user_input.get("location")

    crop_rec = crop_df[crop_df["Crop"].str.lower() == crop.lower()].to_dict(orient="records")
    crop_info = crop_rec[0] if crop_rec else {}
    soil_rec = soil_df[soil_df["Soil_Type"].str.lower() == soil.lower()].to_dict(orient="records")
    soil_info = soil_rec[0] if soil_rec else {}
    region_name = location.split(",")[-1].strip() if location and "," in location else location
    region_rec = region_df[region_df["Region"].str.lower().str.contains(region_name.lower() if region_name else "")].to_dict(orient="records")
    region_info = region_rec[0] if region_rec else {}

    policy_rec = policy_df[policy_df["Region"].str.lower().str.contains(region_name.lower() if region_name else "")].to_dict(orient="records")
    policy_info = policy_rec[0] if policy_rec else {}

    context = {
        "user_input": user_input,
        "crop_info": crop_info,
        "soil_info": soil_info,
        "region_info": region_info,
        "policy_info": policy_info
    }
    return context

def planner_agent(user_input):
    context = build_context(user_input)
    # craft a prompt for the LLM using context
    prompt = f"""
You are an agricultural residue planner. Use this context to generate an initial residue utilization allocation.
Context: {json.dumps(context, indent=2)}
Return JSON with keys: plan (percentages sum to 100), reasoning (text), confidence (0-1).
"""
    resp_text = llm_call_system(prompt)
    try:
        # If response is JSON (as our fallback returns), parse it
        parsed = json.loads(resp_text)
        if "plan" in parsed:
            return parsed
    except Exception:
        # If LLM returned free text, do a minimal parse heuristic (not robust)
        # For starter, return a safe default plan using soil context
        soil = context["soil_info"].get("Soil_Type", "").lower()
        if "clay" in soil:
            plan = {"Compost":45,"Biochar":35,"Biogas":15,"Feed_or_Storage":5}
        else:
            plan = {"Compost":40,"Biochar":30,"Biogas":25,"Feed_or_Storage":5}
        return {"plan":plan, "reasoning":"Default fallback parse used.", "confidence":0.6}
