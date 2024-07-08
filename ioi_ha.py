""" Data organization and analysis for Qualtrics-based IOI-HA results.

    Author: Travis M. Moore
    Created: May 30, 2023
    Last Edited: May 30, 2023
"""

###########
# Imports #
###########
# Import data science packages
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Import GUI packages
import tkinter as tk
from tkinter import filedialog


#######################
# Organize APHAB Data #
#######################
# Individual limits for mild-moderate and mod-severe+ groups
# Tuples include lower and upper limits
ind_mild_dict = {
    1: (3, 5),
    2: (3, 4),
    3: (3, 4),
    4: (2, 4),
    5: (3, 4),
    6: (3, 5),
    7: (3, 4),
}

ind_mod_dict = {
    1: (4.5, 0.96),
    2: (3.52, 1.08),
    3: (3.19, 1.05),
    4: (3.84, 1.17),
    5: (3.38, 1.11),
    6: (3.38, 1.1),
    7: (3.68, 1.02),
}

# Group norms for each subscale for mild-moderate and mod-severe+ groups
# Tuples include mean and SD
group_mild_dict = {
    1: (3.73, 1.17),
    2: (3.39, 0.98),
    3: (3.4, 0.95),
    4: (3.2, 1.21),
    5: (3.57, 1.13),
    6: (3.79, 1.13),
    7: (3.19, 0.93),
}

group_mod_dict = {
    1: (4.5, 0.96),
    2: (3.52, 1.08),
    3: (3.19, 1.05),
    4: (3.84, 1.17),
    5: (3.38, 1.11),
    6: (3.38, 1.1),
    7: (3.68, 1.02),
}


# Import data
root = tk.Tk()
root.withdraw()
# Get path to IOI-HA data
# Must be directly pulled from Qualtrics
filename = filedialog.askopenfilename(
    title="Choose IOI-HA Data File",
    filetypes=[('comma separated', '*.csv')]
)
# Read in data
data_full = pd.read_csv(filename)

# Subset only pertinent data
data = data_full.iloc[2:, 17:].copy()
# Generate new column names
colnames = list(range(1,9))
colnames.insert(0, 'subject')
data.columns = colnames
# Reset index
data.reset_index(inplace=True, drop=True)

# convert values to float (to accommodate NaN)
cols = list(data)[1:]
data[cols] = data[cols].astype(float)

# Assign which norms to use based on reported difficult
# This returns a list of booleans where True == mild-mod
# and False == mod-severe+
bools = data[8] > 2
data.loc[bools, 'difficulty'] = 'mild-mod'
data.loc[bools==False, 'difficulty'] = 'mod-severe'

# Convert from wide to long format
data_long = pd.melt(data, id_vars=['subject', 'difficulty'], value_vars=list(range(1,9)))
#Rename variable column after melt
data_long = data_long.rename(columns={'variable': 'question', 'value': 'score'})
# Reset index
data_long.reset_index(drop=True, inplace=True)


# ####################
# # Calculate scores #
# ####################
# # Subscale scores
# subscale_data = data.groupby(['subject', 'subscale'])['score'].apply(np.mean)
# subscale_data = pd.DataFrame(subscale_data).reset_index()
# print('-' * 60)
# print('APHAB Subscale Scores')
# print('-' * 60)
# print(subscale_data)
# print('-' * 60)
# print('\n')


# # Global scores
# # Drop AV subscale to calculate global score
# global_scores = data.loc[data['subscale'].isin(['BN', 'EC', 'RV'])].copy()
# global_scores = global_scores.groupby(['subject'])['score'].apply(np.mean)
# global_scores = pd.DataFrame(global_scores).reset_index()
# print('-' * 60)
# print('APHAB Global Scores')
# print('-' * 60)
# print(global_scores)
# print('-' * 60)
# print('\n')

# Add column for 
data_long['WNL'] = ''
for row in range(0, len(data_long)):
    try:
        if data_long.loc[row, 'difficulty'] == 'mild_mod':
            norms = ind_mild_dict[data_long.loc[row, 'question']]
        elif data_long.loc[row, 'difficulty'] == 'mod-severe':
            norms = ind_mod_dict[data_long.loc[row, 'question']]
    except KeyError:
        norms = 'error'

    try:
        if (data_long.loc[row, 'score'] <= norms[0]+norms[1]) and \
            (data_long.loc[row, 'score'] >= norms[0]-norms[1]):
            data_long.loc[row, 'WNL'] = 'wnl'
        else: 
            data_long.loc[row, 'WNL'] = 'outside'
    except KeyError:
        data_long.loc[row, 'WNL'] = 'NA'
    except TypeError:
        data_long.loc[row, 'WNL'] = 'NA'


##################
# Create new dfs #
##################
mild_mod = data_long[data_long['difficulty']=='mild-mod'].copy()
mild_mod.reset_index(drop=True, inplace=True)
mod_severe = data_long[data_long['difficulty']=='mod-severe'].copy()
mod_severe.reset_index(drop=True, inplace=True)


#########################
# Box and Whisker Plots #
#########################
# Group scores by question
# MILD-MODERATE
sns.boxplot(data=mild_mod, x='question', y='score')
plt.ylim([0, 6])
plt.title('IOI-HA: Mild-Moderate Group')
plt.show()

# MOD-SEVERE
sns.boxplot(data=mod_severe, x='question', y='score')
plt.ylim([0, 6])
plt.title('IOI-HA: Mod-Severe+ Group')
plt.show()


#############
# Bar Graph #
#############
# Group scores by question
# MILD-MODERATE
sns.barplot(data=mild_mod, x='question', y='score')
plt.ylim([0, 6])
plt.title('IOI-HA: Mild-Moderate Group')

for key in group_mild_dict:
    plt.plot(key-1, group_mild_dict[key][0] + group_mild_dict[key][1], 'go')
    plt.plot(key-1, group_mild_dict[key][0] - group_mild_dict[key][1], 'ro')
plt.show()


# MOD-SEVERE
sns.barplot(data=mod_severe, x='question', y='score')
plt.ylim([0, 6])
plt.title('IOI-HA: Mod-Severe+ Group')

for key in group_mod_dict:
    plt.plot(key-1, group_mod_dict[key][0] + group_mod_dict[key][1], 'go')
    plt.plot(key-1, group_mod_dict[key][0] - group_mod_dict[key][1], 'ro')
plt.show()
plt.show()
