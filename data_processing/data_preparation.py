import pandas as pd
import numpy as np
import os

# Load the dataset
data_path = '../Pre-Super_Day_candidate_dataset.xlsx - Sheet1.csv'  # Adjust this path if needed
data = pd.read_csv(data_path)

# Initialize text summary
text_summary_path = '../dashboard/public/exported_results/text_summary_output.txt'
os.makedirs('exported_results', exist_ok=True)

with open(text_summary_path, 'w') as summary_file:
    # Initial inspection
    summary_file.write("Data preview:\n")
    summary_file.write(data.head().to_string() + "\n\n")

    summary_file.write("Data Info:\n")
    data_info = data.info(buf=summary_file)
    summary_file.write("\n")

# Data Cleaning
data.drop_duplicates(inplace=True)
data.ffill(inplace=True)  # Forward fill for missing data

# Feature Engineering
data['Debt_to_Income'] = data['Monthly_Housing_Payment'] / data['Monthly_Gross_Income']
data['High_FICO'] = np.where(data['FICO_score'] > 700, 1, 0)
fico_order = ["Poor", "Fair", "Good", "Very Good", "Exceptional"]
data['FICO_Score_Group_Encoded'] = pd.Categorical(data['Fico_Score_group'], categories=fico_order, ordered=True).codes
data['Employment_Type'] = data['Employment_Status'].apply(lambda x: 'Unemployed' if x == 'Unemployed' else 'Employed')

loan_reason_mapping = {
    "cover_an_unexpected_cost": "Emergency",
    "credit_card_refinancing": "Refinancing",
    "home_improvement": "Improvement",
    "major_purchase": "Purchase",
    "medical_expense": "Emergency",
    "small_business": "Business",
    "other": "Other"
}
data['Loan_Purpose_Group'] = data['Reason'].map(loan_reason_mapping)
data['Financial_Hardship'] = np.where(data['Ever_Bankrupt_or_Foreclose'] == 1, 1, 0)
data['Income_to_Loan_Ratio'] = data['Monthly_Gross_Income'] / data['Loan_Amount']
data['Revenue_Potential'] = data['bounty'] * data['Approved']

# Summary statistics for each new feature
with open(text_summary_path, 'a') as summary_file:
    summary_file.write("\nDebt-to-Income Ratio Summary:\n")
    summary_file.write(data['Debt_to_Income'].describe().to_string() + "\n\n")

    summary_file.write("Income to Loan Ratio Summary:\n")
    summary_file.write(data['Income_to_Loan_Ratio'].describe().to_string() + "\n\n")

    summary_file.write("Revenue Potential Summary:\n")
    summary_file.write(data['Revenue_Potential'].describe().to_string() + "\n\n")

# Save cleaned and processed data for use in API
processed_data_path = '../dashboard/public/exported_results/processed_data.csv'
data.to_csv(processed_data_path, index=False)
print(f"Processed data saved to {processed_data_path}")
print(f"Text summary saved to {text_summary_path}")
