import io
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate_plot(baseline_path, sample_path, output_path):
    # Read CSVs, skipping first row
    base = pd.read_csv(baseline_path, skiprows=1)
    sample = pd.read_csv(sample_path, skiprows=1)

    # Extract labels for the legend
    base_label = os.path.splitext(os.path.basename(baseline_path))[0]
    sample_label = os.path.splitext(os.path.basename(sample_path))[0]

    # Create figure and plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(base['cm-1'], base['A'], label=base_label, linewidth=1)
    ax.plot(sample['cm-1'], sample['A'], label=sample_label, linewidth=1)

    # Axis labels
    plt.xlabel('cm-1')
    plt.ylabel('A')

    # Legend
    plt.legend(
        loc='lower left',
        bbox_to_anchor=(0, -0.1),
        borderaxespad=0,
        frameon=False
    )

    # Save to output path
    fig.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"✅ Saved plot to {output_path}")
