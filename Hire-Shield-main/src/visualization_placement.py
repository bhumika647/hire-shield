import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot_placement_bias(results, save_path=None):
    plt.figure(figsize=(10, 6))
    for attr, data in results.items():
        if attr == 'overall_bias_detected':
            continue
        groups = list(data['group_metrics'].keys())
        selection_rates = [data['group_metrics'][g]['selection_rate'] for g in groups]
        plt.bar(groups, selection_rates, label=f"{attr} (Disparity: {data['disparity_ratio']:.2f})")
    plt.title("Placement Group-wise Selection Rate Disparities")
    plt.xlabel("Group")
    plt.ylabel("Selection Rate")
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.close()
