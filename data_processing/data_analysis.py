import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency
import os

# Set the style for all plots
plt.style.use('dark_background')

# Custom color palette
colors = ['#60A5FA', '#34D399', '#F87171', '#A78BFA', '#FBBF24']

# Set global text color to white for all plot elements
plt.rcParams.update({
    'text.color': 'white',
    'axes.labelcolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'axes.titlecolor': 'white',
    'figure.facecolor': '#1A202C',
    'axes.facecolor': '#2D3748',
    'axes.edgecolor': 'white',
    'axes.grid': True,
    'grid.color': '#4A5568',
    'grid.alpha': 0.3
})

# Create folder for exporting results if it doesn't exist
export_folder = '../dashboard/public/exported_results'
os.makedirs(export_folder, exist_ok=True)

# Redirect print output to a text file for summary
summary_output_path = os.path.join(export_folder, 'text_summary_output.txt')
with open(summary_output_path, 'a') as summary_file:
    # Load the processed data
    data = pd.read_csv('../dashboard/public/exported_results/processed_data.csv')

    # Part 1: Approvals Analysis
    numeric_data = data.select_dtypes(include=[np.number])
    correlation_matrix = numeric_data.corr()

    # Plot correlation matrix with better spacing
    plt.figure(figsize=(12, 10))
    heatmap = sns.heatmap(correlation_matrix, 
                annot=True, 
                cmap="RdBu_r",
                fmt='.2f',
                square=True,
                cbar_kws={'label': 'Correlation'},
                annot_kws={'size': 8, 'color': 'white'})
    
    # Manually set colorbar label color to white
    heatmap.figure.axes[-1].yaxis.label.set_color('white')
    
    plt.title("Correlation Matrix for Numeric Variables", size=14, pad=20)
    # Adjust subplot parameters for better fit
    plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
    plt.savefig(os.path.join(export_folder, 'correlation_matrix.png'), 
                dpi=300, 
                bbox_inches='tight',
                facecolor='#1A202C')
    plt.close()

    # Part 2: Lender Approval Rates
    fig, ax = plt.subplots(figsize=(12, 7))
    approval_rates_per_lender = data.groupby('Lender')['Approved'].mean()
    bars = approval_rates_per_lender.plot(kind='bar', 
                                        color=colors[0],
                                        ax=ax,
                                        width=0.7)
    
    # Calculate appropriate y-limit
    max_value = approval_rates_per_lender.max()
    plt.ylim(0, max_value * 1.1)  # Add 10% padding for labels
    
    # Add value labels inside the bars at the top
    for i, v in enumerate(approval_rates_per_lender):
        ax.text(i, v * 0.95,  # Position at 95% of bar height
                f'{v:.1%}',
                ha='center',
                va='top',
                color='white',
                fontsize=10)

    plt.title("Approval Rates by Lender", size=14, pad=20)
    plt.xlabel("Lender", labelpad=10)
    plt.ylabel("Approval Rate", labelpad=10)
    
    # Rotate x-axis labels
    plt.xticks(rotation=90)
    
    plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
    plt.savefig(os.path.join(export_folder, 'approval_rates_per_lender.png'),
                dpi=300,
                bbox_inches='tight',
                facecolor='#1A202C')
    plt.close()

    # FICO Score analysis
    fig, ax = plt.subplots(figsize=(14, 7))
    approval_rates_by_fico = data.groupby(['Lender', 'Fico_Score_group'])['Approved'].mean().unstack()
    approval_rates_by_fico.plot(kind='bar',
                              stacked=False,
                              ax=ax,
                              width=0.8)
    
    plt.title("Approval Rates by FICO Score Group", size=14, pad=20)
    plt.xlabel("Lender", labelpad=10)
    plt.ylabel("Approval Rate", labelpad=10)
    # Adjust legend
    plt.legend(title="FICO Score Group", 
              bbox_to_anchor=(1.02, 1),
              loc='upper left',
              borderaxespad=0,
              frameon=True,
              facecolor='#2D3748',
              edgecolor='white',
              labelcolor='white',
              title_fontsize=10)
    # Adjust subplot parameters
    plt.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.15)
    plt.savefig(os.path.join(export_folder, 'approval_rates_by_fico.png'),
                dpi=300,
                bbox_inches='tight',
                facecolor='#1A202C')
    plt.close()

    # Revenue Analysis
    fig, ax = plt.subplots(figsize=(12, 7))
    revenue_per_approved_app = data[data['Approved'] == 1].groupby('Lender')['Revenue_Potential'].mean()
    bars = revenue_per_approved_app.plot(kind='bar',
                                       color=colors[1],
                                       ax=ax,
                                       width=0.7)

    # Calculate appropriate y-limit to accommodate labels
    max_value = revenue_per_approved_app.max()
    plt.ylim(0, max_value * 1.1)  # Add 10% padding for labels

    # Add value labels inside the bars at the top
    for i, v in enumerate(revenue_per_approved_app):
        ax.text(i, v * 0.95,  # Position at 95% of bar height
                f'${v:,.0f}',
                ha='center',
                va='top',
                color='white',
                fontsize=10)

    plt.title("Average Revenue per Approved Application", size=14, pad=20)
    plt.xlabel("Lender", labelpad=10)
    plt.ylabel("Average Revenue ($)", labelpad=10)
    
    # Rotate x-axis labels
    plt.xticks(rotation=90)
    
    plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
    plt.savefig(os.path.join(export_folder, 'revenue_per_approved_app.png'),
                dpi=300,
                bbox_inches='tight',
                facecolor='#1A202C')
    plt.close()

    # High-value segments
    fig, ax = plt.subplots(figsize=(12, 7))
    high_value_segments = data[data['High_FICO'] == 1].groupby('Lender')['Revenue_Potential'].mean()
    bars = high_value_segments.plot(kind='bar',
                                  color=colors[2],
                                  ax=ax,
                                  width=0.7)

    # Calculate appropriate y-limit
    max_value = high_value_segments.max()
    plt.ylim(0, max_value * 1.1)  # Add 10% padding for labels
    
    # Add value labels inside the bars at the top
    for i, v in enumerate(high_value_segments):
        ax.text(i, v * 0.95,  # Position at 95% of bar height
                f'${v:,.0f}',
                ha='center',
                va='top',
                color='white',
                fontsize=10)

    plt.title("High FICO Score Segment - Average Revenue", size=14, pad=20)
    plt.xlabel("Lender", labelpad=10)
    plt.ylabel("Average Revenue ($)", labelpad=10)
    
    # Rotate x-axis labels
    plt.xticks(rotation=90)
    
    plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
    plt.savefig(os.path.join(export_folder, 'high_value_segments.png'),
                dpi=300,
                bbox_inches='tight',
                facecolor='#1A202C')
    plt.close()
    

    # DTI Analysis
    fig, ax = plt.subplots(figsize=(14, 7))
    data['Debt_to_Income_Segment'] = pd.cut(data['Debt_to_Income'],
                                          bins=[0, 0.2, 0.4, 0.6, 0.8, 1, float('inf')],
                                          labels=['<0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0', '>1.0'])
    
    approval_rates_dti = data.groupby(['Debt_to_Income_Segment', 'Lender'])['Approved'].mean().unstack()
    approval_rates_dti.plot(kind='bar',
                          stacked=False,
                          ax=ax,
                          width=0.8)

    plt.title("Approval Rates by Debt-to-Income Ratio", size=14, pad=20)
    plt.xlabel("Debt-to-Income Segment", labelpad=10)
    plt.ylabel("Approval Rate", labelpad=10)
    # Adjust legend
    plt.legend(title="Lender",
              bbox_to_anchor=(1.02, 1),
              loc='upper left',
              borderaxespad=0,
              frameon=True,
              facecolor='#2D3748',
              edgecolor='white',
              labelcolor='white',
              title_fontsize=10)
    # Adjust subplot parameters
    plt.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.15)
    plt.savefig(os.path.join(export_folder, 'approval_rates_by_dti.png'),
                dpi=300,
                bbox_inches='tight',
                facecolor='#1A202C')
    plt.close()

    # Income to Loan Analysis
    data['Income_to_Loan_Segment'] = pd.cut(data['Income_to_Loan_Ratio'],
                                          bins=[0, 0.1, 0.3, 0.5, 1, float('inf')],
                                          labels=['<0.1', '0.1-0.3', '0.3-0.5', '0.5-1.0', '>1.0'])
    
    revenue_by_income_loan_fico = data.groupby(['Income_to_Loan_Segment', 'High_FICO', 'Lender'])['Revenue_Potential'].mean().unstack()
    
    if 1 in revenue_by_income_loan_fico.index.get_level_values('High_FICO'):
        fig, ax = plt.subplots(figsize=(14, 7))
        revenue_by_income_loan_fico.xs(1, level='High_FICO').plot(kind='bar',
                                                                 stacked=False,
                                                                 ax=ax,
                                                                 width=0.8)
        
        plt.title("Revenue by Income-to-Loan Ratio (High FICO)", size=14, pad=20)
        plt.xlabel("Income-to-Loan Segment", labelpad=10)
        plt.ylabel("Average Revenue ($)", labelpad=10)
        # Adjust legend
        plt.legend(title="Lender",
                  bbox_to_anchor=(1.02, 1),
                  loc='upper left',
                  borderaxespad=0,
                  frameon=True,
                  facecolor='#2D3748',
                  edgecolor='white',
                  labelcolor='white',
                  title_fontsize=10)
        # Adjust subplot parameters
        plt.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.15)
        plt.savefig(os.path.join(export_folder, 'revenue_by_income_to_loan_fico.png'),
                    dpi=300,
                    bbox_inches='tight',
                    facecolor='#1A202C')
        plt.close()

print("Data analysis completed with improved dark theme visualizations. Results saved in 'exported_results'.")