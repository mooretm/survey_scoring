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
colnames.insert(0, 'subject')
data.columns = colnames

question_key = [20,14,18,7,11,15,6,13,12,16,17,24,5,8,10,2,23,3,21,1,19,22,4,9]

new = data[question_key]
new.to_csv('reordered-WITHOUT.csv', index=False)
