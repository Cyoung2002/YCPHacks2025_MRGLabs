import pandas as pd
import matplotlib.pyplot as plt
import os

def create_demo_plot(baseline, sampleData):

    # Reading the imported csv files, skipping the first row since it is not needed data
    base = pd.read_csv(baseline, skiprows=1)
    sample = pd.read_csv(sampleData, skiprows=1)

    # Extract filenames (without .csv) for legend labels
    base_label = os.path.splitext(os.path.basename(baseline))[0]
    sample_label = os.path.splitext(os.path.basename(sampleData))[0]

    # Plotting the data from the csv, will need to dynamically pull the names from the files later
    plt.plot(base['cm-1'], base['A'], label=base_label, linewidth=1)
    plt.plot(sample['cm-1'], sample['A'], label=sample_label, linewidth=1)

    # Axis labels
    plt.xlabel('cm-1')
    plt.ylabel('A')

    # Creating legend for plot
    plt.legend(
        loc='lower left',
        bbox_to_anchor=(0, -0.1),
        borderaxespad=0,
        frameon=False
    )

    # Generating the plot
    plt.show()