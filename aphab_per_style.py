""" Data organization and analysis for Qualtrics-based APHAB results.
    
    Returns CSV files for subscale and global scores for each style. 

    Author: Travis M. Moore
    Created: 10/19/2022
    Last Edited: March 26, 2024
"""

###########
# Imports #
###########
# Data
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# GUI
import tkinter as tk
from tkinter import filedialog

# System
import os

#############
# Functions #
#############
def score_aphab(data):
    """ Score APHAB data by form factor.
    
        :param data: a Pandas DataFrame in long format.

        :returns: CSV files with subscale and global scores, and plots
    """
    # Create copy of full data set
    all_styles = data.copy()

    # Get unique hearing aid styles from df
    unique_styles = all_styles['style'].unique()

    # Subset single style into new df
    for style in unique_styles:
        mask = all_styles['style'] == style
        data = all_styles[mask].copy()
        data.reset_index(inplace=True)

        # Create subscales from question numbers
        EC = [4, 10, 12, 14, 15, 23]
        BN = [1, 6, 7, 16, 19, 24]
        RV = [2, 5, 9, 11, 18, 21]
        AV = [3, 8, 13, 17, 20, 22]

        # Create subscale column
        data['subscale'] = np.repeat(0,len(data))
        for ii in range(0, len(data)):
            if data['q_num'][ii] in EC:
                data.loc[ii, 'subscale'] = 'EC'
            elif data['q_num'][ii] in BN:
                data.loc[ii, 'subscale'] = 'BN'
            elif data['q_num'][ii] in RV:
                data.loc[ii, 'subscale'] = 'RV'
            elif data['q_num'][ii] in AV:
                data.loc[ii, 'subscale'] = 'AV'

        ##############
        # Clean Data #
        ##############
        # Identify subscales when fewer than 2/3 of a specific subscale's 
        # questions were answered (i.e., can only miss 2 questions).
        missing_data = []
        msg = "Subscale Errors"
        print('-' * 60)
        print(msg)
        print('-' * 60)
        for sub in data['subject'].unique():
            single_sub_df = data[data['subject'] == sub]
            for s in single_sub_df['subscale'].unique():
                #print(f"\nTesting subscale {s}")
                bools = single_sub_df['subscale'] == s
                temp = single_sub_df[bools]
                #print(temp)
                x = temp['value'].isnull().sum()
                #print(f"x: {x}")
                if x > 2:
                    print(f"Subject {sub} has more than two missing questions for {s}")
                    missing_data.append((sub, s))

        # Remove subscales with insufficient data
        print(f"\nLength of DF before cleaning: {len(data)}")
        for subject, subscale in missing_data:
            bools = (data['subject']==subject) & (data['subscale']==subscale)
            data = data[-bools]
        print(f"Length of DF after cleaning: {len(data)}")
        print('-' * 60)

        ####################
        # Calculate Scores #
        ####################
        # Subscale scores
        subscale_data = data.groupby(['subject', 'subscale'])['score'].apply(np.mean)
        subscale_data = pd.DataFrame(subscale_data).reset_index()
        print('')
        print('-' * 60)
        print('APHAB Subscale Scores')
        print('-' * 60)
        print(subscale_data)
        print('-' * 60)
        print('')
        # Save to .csv
        subscale_out = style + '_SUBSCALE_' + os.path.split(filename)[1]
        subscale_data.to_csv(subscale_out, index=False)


        # Global scores
        # Drop AV subscale to calculate global score
        global_scores = data.loc[data['subscale'].isin(['BN', 'EC', 'RV'])].copy()
        global_scores = global_scores.groupby(['subject'])['score'].apply(np.mean)
        global_scores = pd.DataFrame(global_scores).reset_index()
        print('-' * 60)
        print('APHAB Global Scores')
        print('-' * 60)
        print(global_scores)
        print('-' * 60)
        print('')
        # Save to .csv
        global_out = style + '_GLOBAL_' + os.path.split(filename)[1]
        global_scores.to_csv(global_out, index=False)

        #########################
        # Box and Whisker Plots #
        #########################
        # Group subscale scores
        sns.boxplot(data=subscale_data, x='subscale', y='score')
        plt.ylim([0, 100])
        plt.title('Average APHAB Subscale Scores')
        plt.show()
        plt.close()

        # Group global scores
        sns.boxplot(data=global_scores)
        plt.title('Average APHAB Global Score')
        plt.ylim([0, 100])
        plt.show()
        plt.close()


#######
# RUN #
#######
#############
# Constants #
#############
STYLES={
    1: 'RIC_RT', 
    2: 'RIC_312', 
    3: 'mRIC_R',
    4: 'ITE_R',
    5: 'ITC_R', 
    6: 'CIC_312', 
    7: 'WiCROS'
}

#######################
# Organize APHAB Data #
#######################
root = tk.Tk()
root.withdraw()
# Get path to APHAB data
filename = filedialog.askopenfilename(
    title="Choose APHAB Data File",
    filetypes=[('comma separated', '*.csv')]
)
# Read in data
data_full = pd.read_csv(filename)

# # For testing: load in data from static path
# data_full = pd.read_csv('test_data.csv')
# filename = './test_data.csv'

# Subset only pertinent data
data = data_full.iloc[2:, 17:].copy()

# Generate new column names
colnames = list(range(1,25))
colnames.insert(0, "subject")
colnames.insert(1, "style")

# Apply new column names
data.columns = colnames

# Replace style values with names from dict
for ii, style in enumerate(data['style']):
    data.iloc[ii, 1] = STYLES[int(style)]

# Convert from wide to long format
data = pd.melt(data, id_vars=['subject', 'style'], value_vars=list(range(1,25)))

# Rename variable column after melt
data = data.rename(columns={'variable': 'q_num'})

# Convert to float to accommodate NaNs
data['value'] = data['value'].astype(float)


######################
# Create new columns #
######################
# Identify reversed questions
data['reversed'] = data['q_num'].isin([1, 16, 19, 9, 11, 21])

# Create scoring key dict for normal and reversed questions
scores = [99, 87, 75, 50, 25, 12, 1]

# Non-revsered dictionary
not_reversed_score = {}
for idx, score in enumerate(scores, start=1):
    not_reversed_score[idx] = score
scores.reverse()
# Reversed dictionary
reversed_score = {}
for idx, score in enumerate(scores, start=1):
    reversed_score[idx] = score

# Create converted score column
data['score'] = np.where(
    data['reversed']==True, # condition
    data['value'].map(reversed_score), # if True
    data['value'].map(not_reversed_score) # if False
    )

# Reset index
data.reset_index(inplace=True)

# Output to console
print(f"Organized data:\n{data}")

# Call scoring function
score_aphab(data=data)
