# optimizer.py
import json
from core.llm_adapter import llm_call_system
from core.kb_loader import load_regional_data, load_policy_data, load_crop_data

def optimize_plan(initial_plan_obj):
    """
    initial_plan_obj: dict containing plan, user_input, possibly reasoning
    Returns final optimized plan dict
    """
    # Extract
    plan = initial_plan_obj.get("plan", {})
    user_input = initial_plan_obj.get("user_input", {})
    location = user_input.get("location", "")
    region_name = location.split(",")[-1].strip() if "," in location else location

    # Retrieve KB data that optimizer needs
    region_df = load_regional_data()
    policy_df = load_policy_data()

    region_rec = region_df[region_df["Region"].str.lower().str.contains(region_name.lower() if region_name else "")].to_dict(orient="records")
    region_info = region_rec[0] if region_rec else {}
    policy_rec = policy_df[policy_df["Region"].str.lower().str.contains(region_name.lower() if region_name else "")].to_dict(orient="records")
    policy_info = policy_rec[0] if policy_rec else {}

    # Build a simple rules-based check first
    biochar_limit = region_info.get("Biochar_Max_pct", 30)
    compost_capacity = region_info.get("Compost_Capacity_t_per_day", None)
    biogas_subsidy = region_info.get("Biogas_Subsidy_pct", policy_info.get("Biogas_Subsidy_pct", 0))

    adjusted_plan = plan.copy()

    # Ensure percentages exist and sum to 100 (normalize if necessary)
    total = sum(adjusted_plan.values()) if adjusted_plan else 0
    if total == 0:
        adjusted_plan = {"Compost":50,"Biochar":30,"Biogas":15,"Feed_or_Storage":5}
        total = 100
    if total != 100:
        # normalize respecting existing ratio
        adjusted_plan = {k: round(v * 100.0 / total, 1) for k, v in adjusted_plan.items()}

    # Enforce biochar limit
    if adjusted_plan.get("Biochar", 0) > biochar_limit:
        diff = adjusted_plan["Biochar"] - biochar_limit
        adjusted_plan["Biochar"] = biochar_limit
        # shift diff to compost (or to biogas)
        adjusted_plan["Compost"] = adjusted_plan.get("Compost",0) + diff

    # If biogas subsidy is high, nudge allocation
    if biogas_subsidy and biogas_subsidy >= 20:
        # increase biogas by 5% if feasible, reduce compost slightly
        inc = 5
        adjusted_plan["Biogas"] = min( adjusted_plan.get("Biogas",0) + inc, 40 )
        adjusted_plan["Compost"] = max(0, adjusted_plan.get("Compost",0) - inc)

    # Final normalization to integer percents
    keys = list(adjusted_plan.keys())
    vals = adjusted_plan
    total = sum([vals[k] for k in keys])
    if total != 100:
        # normalize again
        adjusted_plan = {k: int(round(vals[k] * 100.0 / total)) for k in keys}
        # fix rounding remainder
        r = 100 - sum(adjusted_plan.values())
        if r != 0:
            adjusted_plan[keys[0]] += r

    # Calculate simple sustainability metrics using KB heuristics (toy calc)
    # In a real implementation this would call the KB for CO2 factors, prices, etc.
    co2_reduction_pct = 0.0
    # heuristics: weights per method
    weights = {"Compost":0.4, "Biochar":0.7, "Biogas":0.3, "Feed_or_Storage":0.0}
    for k,v in adjusted_plan.items():
        co2_reduction_pct += weights.get(k,0) * v / 100.0 * 100.0
    # crude ROI estimate
    revenue = adjusted_plan.get("Compost",0)*30 + adjusted_plan.get("Biochar",0)*50 + adjusted_plan.get("Biogas",0)*20 + adjusted_plan.get("Feed_or_Storage",0)*5
    # build final output
    out = {
        "Final_Optimized_Plan": adjusted_plan,
        "Sustainability_Impact": {
            "Residue_Utilized_%": 100,
            "CO2_Reduction_%": round(co2_reduction_pct,1),
            "Soil_Health_Score": round(6.0 + adjusted_plan.get("Compost",0)/10.0,1)
        },
        "Economic_Impact": {
            "Total_Revenue_EST": int(revenue * 100),  # toy unit
            "Cost_Efficiency_Score": round(0.8 + (adjusted_plan.get("Biochar",0)/100.0)*0.1,2)
        },
        "Optimizer_Reasoning": f"Adjusted plan based on regional biochar limit {biochar_limit}% and biogas subsidy {biogas_subsidy}%.",
        "Confidence_Score": 0.9
    }
    return out
