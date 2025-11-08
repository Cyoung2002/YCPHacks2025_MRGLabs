import pandas as pd
import matplotlib.pyplot as plt
import os
import io

def create_demo_plot(baseline, sampleData):

    # Reading the imported csv files, skipping the first row since it is not needed data
    base = pd.read_csv(baseline, skiprows=1)
    sample = pd.read_csv(sampleData, skiprows=1)

    # Extract filenames (without .csv) for legend labels
    base_label = os.path.splitext(os.path.basename(baseline))[0]
    sample_label = os.path.splitext(os.path.basename(sampleData))[0]

    # Create plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(base['cm-1'], base['A'], label=base_label, linewidth=1)
    ax.plot(sample['cm-1'], sample['A'], label=sample_label, linewidth=1)

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
    # plt.show()

    # Save figure to an in-memory buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)  # rewind to start so it can be read

    print(f"✅ Created plot for: {base_label} vs {sample_label}")
    return buffer  # returns an in-memory PNG image object