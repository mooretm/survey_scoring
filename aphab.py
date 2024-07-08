""" Data organization and analysis for Qualtrics-based APHAB results.

I.	Use Travis’ APHAB with added form factor column
A.	Collect data once for WITHOUT hearing aids
1.	DO NOT include the last three questions
2.	Export, and include “without” in the CSV file name
B.	Collect data once for WITH hearing aids
1.	DO NOT include the last three questions
2.	Export, and include the form factor and “with” in the CSV file name


II.	Coding
A.	Modify with logic to check for column length
1.	Because one survey will have the last three questions and one won’t
B.	Modify column numbers to accommodate form factor column
C.	Modify to score by form factor 
1.	To avoid running by hand for each form factor

    Author: Travis M. Moore
    Created: 10/19/2022
    Last Edited: Jan 25, 2024
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Import GUI packages
import tkinter as tk
from tkinter import filedialog


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


# Subset only pertinent data
data = data_full.iloc[2:, 17:].copy()
# Generate new column names
colnames = list(range(1,28))
#colnames = list(range(1,25))
colnames.insert(0, 'subject')
data.columns = colnames
# Convert from wide to long format
data = pd.melt(data, id_vars='subject', value_vars=list(range(1,28)))
#data = pd.melt(data, id_vars='subject', value_vars=list(range(1,25)))
# Rename variable column after melt
data = data.rename(columns={'variable': 'q_num'})

# Convert responses to integers
#data['value'] = data['value'].astype(int)
# Convert to float to accommodate NaNs
data['value'] = data['value'].astype(float)

# Retain only questions 1:24
data = data[data['q_num'].isin(range(0,25))]


######################
# Create new columns #
######################
# Identify reversed questions
data['reversed'] = data['q_num'].isin([1, 16, 19, 9, 11, 21])

# Create scoring key dict for
# reversed and not reversed questions
scores = [99, 87, 75, 50, 25, 12, 1]
not_reversed_score = {}
for idx, score in enumerate(scores, start=1):
    not_reversed_score[idx] = score
scores.reverse()
reversed_score = {}
for idx, score in enumerate(scores, start=1):
    reversed_score[idx] = score

# Create converted score column
data['score'] = np.where(
    data['reversed']==True, # condition
    data['value'].map(reversed_score), # if True
    data['value'].map(not_reversed_score) # if False
    )

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

# Identify subscales where fewer than 2/3 questions were answered.
# I.E., can only miss 2 questions.
missing_data = []
msg = "Subscales with Insufficient Data"
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
# Calculate scores #
####################
# Subscale scores
subscale_data = data.groupby(['subject', 'subscale'])['score'].apply(np.mean)
subscale_data = pd.DataFrame(subscale_data).reset_index()
print('\n')
print('-' * 60)
print('APHAB Subscale Scores')
print('-' * 60)
print(subscale_data)
print('-' * 60)
print('\n')
# Save to .csv
subscale_out = filename.split('/')[-1][:-4] + '_SUBSCALE.csv'
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
print('\n')
# Save to .csv
global_out = filename.split('/')[-1][:-4] + '_GLOBAL.csv'
global_scores.to_csv(global_out, index=False)


#########################
# Box and Whisker Plots #
#########################
# Group subscale scores
sns.boxplot(data=subscale_data, x='subscale', y='score')
plt.ylim([0, 100])
plt.title('Average APHAB Subscale Scores')
plt.show()

# Group global scores
sns.boxplot(data=global_scores)
plt.title('Average APHAB Global Score')
plt.ylim([0, 100])
plt.show()
