"""Export research previews from retained tables. SPDX-License-Identifier: MIT."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Regenerate the AURA-Q README's standalone SVG previews")
    parser.add_argument("--output", type=Path, default=Path("assets/results"))
    parser.add_argument("--qa-output", type=Path, help="Optional directory for PNG layout-review copies")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output if args.output.is_absolute() else root / args.output
    if output.resolve().is_relative_to((root / "data").resolve()):
        parser.error("Output must be outside frozen data/")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        parser.error('Plotting needs the optional dependency: python -m pip install -e ".[plots]"')
    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":11,
                         "axes.spines.top":False, "axes.spines.right":False,
                         "axes.edgecolor":"#657783", "axes.labelcolor":"#243f50",
                         "xtick.color":"#536774", "ytick.color":"#536774",
                         "svg.fonttype":"none", "svg.hashsalt":"aura-q-v1.1.0"})
    output.mkdir(parents=True, exist_ok=True)
    qa = args.qa_output
    if qa:
        qa = qa if qa.is_absolute() else root / qa
        if qa.resolve().is_relative_to((root / "data").resolve()):
            parser.error("QA output must be outside frozen data/")
        qa.mkdir(parents=True, exist_ok=True)
    source_dir = root / "data/figure_tables"
    provenance = {"renderer":"Matplotlib " + matplotlib.__version__, "files":[],
                  "scope":"Plots of retained table values; no historical experiment or confidence interval rerun"}

    def read(name):
        path = source_dir / name
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return path, list(csv.DictReader(stream))

    def save(fig, name, source, description):
        target = output / (name + ".svg")
        fig.savefig(target, format="svg", bbox_inches="tight", facecolor="white",
                    metadata={"Date":None, "Creator":None, "Description":description})
        if qa:
            fig.savefig(qa / (name + ".png"), dpi=160, bbox_inches="tight", facecolor="white")
        provenance["files"].append({"output":target.name,
            "output_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
            "source":source.relative_to(root).as_posix(),
            "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "description":description})
        plt.close(fig)

    source, rows = read("intent_model_comparison.csv")
    rows = sorted(rows, key=lambda r:float(r["profile_macro_f1"]))
    labels = {"Keyword":"Keyword baseline", "Qwen":"Guarded Qwen", "Mistral":"Guarded Mistral"}
    values = [float(r["profile_macro_f1"]) for r in rows]
    fig, ax = plt.subplots(figsize=(8.4, 3.4))
    fig.subplots_adjust(bottom=0.23)
    ax.barh([labels[r["model"]] for r in rows], values, height=0.55, color="#175e87")
    for i, value in enumerate(values):
        ax.text(value-0.018, i, f"{value:.3f}", va="center", ha="right", color="white", fontweight="bold")
    ax.set_xlim(0, 1)
    ax.set_xlabel("Profile macro-F1")
    ax.set_title("Intent classification on 50 curated requests", loc="left", pad=16, color="#16354a", fontweight="bold")
    ax.set_axisbelow(True)
    ax.grid(axis="x", color="#e5ebef", linewidth=0.8)
    fig.text(0.125, 0.035, "Archived component scores; classification is not rerun by these utilities.", fontsize=10, color="#536774")
    save(fig, "intent_scores", source, "Reported profile macro-F1 on 50 author-curated requests; zero-based scale; no invented intervals.")

    source, rows = read("one_parameter_sensitivity.csv")
    x = [float(r["time_weight"]) for r in rows]
    y = [float(r["aura_minus_shortest_queue_regret"]) for r in rows]
    low = [float(r["ci_low"]) for r in rows]
    high = [float(r["ci_high"]) for r in rows]
    fig, ax = plt.subplots(figsize=(8.4, 4.3))
    fig.subplots_adjust(bottom=0.23)
    ax.fill_between(x, low, high, color="#d6e5ef", label="Retained interval endpoints")
    ax.plot(x, y, marker="o", color="#175e87", linewidth=1.8, markersize=5, label="Recorded mean difference")
    ax.axhline(0, color="#657783", linestyle="--", linewidth=1)
    ax.set_xticks(x)
    ax.set_xlabel("Time weight (quality weight = 0.2; cost is residual)")
    ax.set_ylabel("AURA-Q − shortest-queue regret")
    ax.set_title("Exploratory preference sensitivity", loc="left", pad=16, color="#16354a", fontweight="bold")
    ax.grid(axis="y", color="#e5ebef", linewidth=0.8)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    fig.text(0.125, 0.035, "Negative values favor AURA-Q under the recorded replay objective. Intervals are not recomputed.", fontsize=9, color="#536774")
    save(fig, "preference_sensitivity", source, "Exploratory AURA-Q minus shortest-queue regret; quality weight 0.2; stored low/high endpoints.")
    (output / "PLOT_PROVENANCE.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status":"EXPORTED", "svg_files":len(provenance["files"]), "sources":[x["source"] for x in provenance["files"]]}))


if __name__ == "__main__":
    main()
