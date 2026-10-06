# -*- coding: utf-8 -*-
from google import genai
import json
from google.genai import types,errors
from dotenv import load_dotenv
import os
import httpx

load_dotenv()

def generate_scr_narrative(findings) :
    try:
        sys_instruction = '''You are a senior data analyst writing for Mamaearth's
        regional ops and finance heads. Create a formal narrrative that should return
        only three labeled sections namely Situation, Complication, Resolution. Make sure that every
        number in the output comes from the supplied findings and appear with the same value.
        Do not generate a value of your own.'''

        user_prompt = f'''Below are some of the findings that are found as part of the analysis
        of the orders, products and customers data of Mamaearth. Evaluate them and generate a
        narrative in about 250 words:\n {findings}'''
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {
                "status": "error",
                "narrative": None,
                "message": "GOOGLE_API_KEY not found. Skipping Gemini generation."
            }
        client = genai.Client(api_key = api_key)
        response = client.models.generate_content(
            model = "gemini-3.1-flash-lite",
            contents = f"{user_prompt}",
            config = types.GenerateContentConfig(
              system_instruction = sys_instruction,
              temperature = 0.0, #deterministic as this is a factual business report, not creative writing
              max_output_tokens = 300,
              http_options = types.HttpOptions(
                  timeout = 12000
              )
            )
        )
        return {"status": "success",
                "narrative": response.text,
                "tokens": response.usage_metadata.total_token_count}
        print( response)
    except (errors.APIError, httpx.ConnectError) as e:
        return {"status": "error",
                "narrative": None,
                "message": str(e)}

def generate_scr_narrative_offline(findings):
    offline_narrative = (f'''Situation : Mamaearth’s recent financial performance analysis
reveals a raw total revenue of {findings["raw_total_revenue_inr"]} INR. After rigorous data cleaning and the
reconciliation of duplicate entries—which accounted for a delta of {findings["duplicate_reconciliation_delta_inr"]} INR—the
verified total revenue stands at {findings["cleaned_total_revenue_inr"]} INR. Performance peaked in March 2026, which
represents the true peak month with a revenue of {findings["true_peak_month"]["revenue_inr"]} INR.
Complication : Data integrity challenges were identified, specifically regarding
the month of January 2026. While the apparent revenue was reported at {findings["outlier_inflated_month"]["apparent_revenue_inr"]} INR,
outlier analysis necessitated a correction to {findings["outlier_inflated_month"]["corrected_revenue_inr"]} INR. Furthermore, operational
profitability is being undermined by high return rates, which vary significantly by
payment method: {findings["return_rate_by_payment"]["COD"]}% for COD, {findings["return_rate_by_payment"]["UPI"]}% for UPI, and {findings["return_rate_by_payment"]["CARD"]}% for CARD. The most critical
risk segment involves COD transactions within Tier 2 cities, where the return rate
escalates to {findings["highest_risk_segment"]["return_rate_pct"]}%.
Resolution : To stabilize regional operations and improve financial accuracy,
we must prioritize the mitigation of high-risk COD transactions in Tier 2 cities.
By addressing the {findings["highest_risk_segment"]["return_rate_pct"]}% return rate in this segment and aligning reporting processes
to account for the {findings["duplicate_reconciliation_delta_inr"]} INR reconciliation delta, we can ensure future revenue
reporting remains consistent with the verified {findings["cleaned_total_revenue_inr"]} INR baseline. Moving forward,
incentivizing digital payment methods will be essential to reduce the overall return rate
and protect margins.''')
    offline_narrative = offline_narrative.replace("\n", " ")
    return {"status": "success",
            "narrative": offline_narrative,
            "tokens": None}

def validate_numbers(narrative):
    checker_list = {"total revenue": "97358.3",
                    "COD return rate": "44.4",
                    "highest risk segment return rate":"54.5",
                    "duplicate driven reconciliation delta": "2501.9",
                    "true peak month": "20318.9"}
    for (key,val) in checker_list.items():
        if(val in narrative):
            print(f"The check passed for {key} : {val}")
        else:
            print(f"The check failed for {key} : {val}")

def get_findings():
    findings = {}
    try:
        with open("findings.json", "r") as file:
            findings = json.load(file)
        return(findings)
    except(e):
        print("file not found error :",e)

findings = get_findings()
response_online = generate_scr_narrative(findings)
print("The online response :\n",response_online)
response_offline = {}
narrative = ""
if(response_online["status"] == "error"):
    response_offline = generate_scr_narrative_offline(findings)
    print("The offline response :\n",response_offline)
    narrative = response_offline["narrative"]
else:
    try:
        with open("sample_output.txt","r") as file:
            narrative = file.read()
    except e:
        print("Failed to get Narrative : ",str(e))
validate_numbers(narrative)


