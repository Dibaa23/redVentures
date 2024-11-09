import os
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import json

# Load environment variables
load_dotenv()

# Set your OpenAI API key
api_key = os.getenv('REACT_APP_OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# File paths
export_folder = '../dashboard/public/exported_results'
processed_data_path = '../dashboard/public/exported_results/processed_data.csv'
text_summary_path = os.path.join(export_folder, 'text_summary_output.txt')
image_urls_path = os.path.join(export_folder, 'image_urls.json')

# Load processed data and text summary
with open(processed_data_path, 'r') as file:
    processed_data = file.read()
with open(text_summary_path, 'r') as file:
    text_summary = file.read()

# Load image URLs from JSON file
try:
    with open(image_urls_path, 'r') as file:
        image_urls = json.load(file)
except Exception as e:
    print("Error loading image URLs:", e)
    image_urls = {}

# Define essential and optional visuals using URLs from the JSON
essential_visuals = [
    image_urls.get('approval_rates_per_lender.png', ''),
    image_urls.get('correlation_matrix.png', ''),
    image_urls.get('revenue_per_approved_app.png', '')
]

optional_visuals = [
    image_urls.get('approval_rates_by_fico.png', ''),
    image_urls.get('approval_rates_dti.png', ''),
    image_urls.get('high_value_segments.png', ''),
    image_urls.get('revenue_by_income_loan_fico.png', '')
]

# Helper function to call OpenAI API for ChatCompletion
def call_openai_api(messages):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        max_tokens=1500,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

# --- Call 1: Initial Insights and High-Level Summary ---
print("Running Call 1: Initial Insights and High-Level Summary")

call_1_messages = [
    {"role": "system", "content": "You are a data analyst specialized in business insights."},
    {"role": "user", "content": f"""
You are assisting with business insights from a dataset on loan approvals, focusing on approval rates, revenue potential, and key factors influencing approval. 

Here’s the data and summary of initial analysis, including key visualizations and statistical summaries:
- Text Summary: {text_summary}
- Essential Visuals: {essential_visuals}
- Processed Data Sample: {processed_data[:1000]}  # Limit to 1000 characters for prompt

Please analyze this data and provide high-level insights. Specifically:
1. Summarize the most critical insights related to approval rates and revenue potential.
2. Identify any patterns valuable for business strategy, focusing on factors like FICO scores and debt-to-income ratios.
3. Offer any preliminary recommendations based on these observations.
"""},
]

call_1_result = call_openai_api(call_1_messages)
print("Call 1 Result:")
print(call_1_result)

# --- Call 2: Deeper Analysis for Detailed Insights and Recommendations ---
print("Running Call 2: Deeper Analysis for Detailed Insights and Recommendations")

call_2_messages = [
    {"role": "system", "content": "You are a data analyst specialized in business insights."},
    {"role": "user", "content": f"""
Based on the initial insights, we are now looking for a deeper analysis. Here is additional data, including segmentation by FICO score, debt-to-income ratios, and revenue potential across customer segments.

- Text Summary: {text_summary}
- Optional Visuals: {optional_visuals}
- Processed Data Sample: {processed_data[:1000]}  # Limit to 1000 characters

Please conduct a more detailed analysis. Focus on:
1. Identifying customer segments that may benefit from specific lender matching for improved approval rates or higher revenue per application.
2. Exploring revenue optimization opportunities by matching lenders to high-potential customer groups.
3. Any nuanced insights related to debt-to-income ratios, FICO scores, and income-to-loan ratios that may affect approval likelihood and revenue.
4. Highlight any strategic recommendations based on this deeper analysis that would help refine the business strategy.
"""},
]

call_2_result = call_openai_api(call_2_messages)
print("Call 2 Result:")
print(call_2_result)

# --- Call 3: Merge and Format Comprehensive Findings ---
print("Running Call 3: Merge and Format Comprehensive Findings")

call_3_messages = [
    {"role": "system", "content": "You are an expert data analyst summarizing findings for business leaders."},
    {"role": "user", "content": f"""
Using the previous insights and analyses, create a cohesive report that combines both high-level and detailed findings into a single, structured analysis.

- Call 1 Summary: {call_1_result}
- Call 2 Analysis: {call_2_result}

Structure the report with:
1. An **Executive Summary**: Briefly summarize the key findings, insights, and business implications.
2. **Detailed Analysis**: Break down findings from both the initial and deeper analyses, organized by approval rates, revenue insights, and customer segmentation.
3. **Strategic Recommendations**: Provide actionable recommendations based on the findings, especially focusing on optimized lender matching, potential revenue gains, and strategic areas for improvement.

Ensure the language is accessible to business analysts and non-technical stakeholders, emphasizing the business value of each recommendation.
"""},
]

call_3_result = call_openai_api(call_3_messages)
print("Call 3 Result:")
print(call_3_result)

# Save Call 3 Result
with open(os.path.join(export_folder, 'call_3_result.txt'), 'w') as file:
    file.write(call_3_result)

# Save Call 3 Result as output.json
output_data = {
    "executive_summary": call_3_result
}

with open('output.json', 'w') as json_file:
    json.dump(output_data, json_file)
    
print("All insights generated and saved to the 'exported_results' folder.")
print("Final insights saved to output.json")
