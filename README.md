# COMP-1818 EvoNIDS — Public coursework evidence

**[Full lecturer evidence guide](COMP1818_EvoNIDS_Submission/docs/ONLINE_EXPERIMENTS.md)** · **[Primary results and experiment index](COMP1818_EvoNIDS_Submission/results/README.md)** · **[Latest editable LaTeX report](COMP1818_EvoNIDS_Submission/report/latex/COMP1818_EvoNIDS_LaTeX/main.tex)** · **[Compiled LaTeX PDF](COMP1818_EvoNIDS_Submission/report/latex/COMP1818_EvoNIDS_LaTeX/main.pdf)** · **[Setup and tests](COMP1818_EvoNIDS_Submission/README.md)**

The corrected UNSW-NB15 comparison uses GA, BPSO, PSO and NSGA-II across five matched random seeds and 300 unique classifier evaluations per method and seed. The highest corrected **joint feature-selection + RF hyperparameter** mean test Macro-F1 is **PSO 0.881373**, with **72.86%** mean feature reduction. Results are public recorded measurements, **not** live network-detection predictions. Exact Wilcoxon p=0.0625 for the PSO paired gain; treat five-seed significance claims cautiously.

## Visual evidence (works without GitHub Pages)

![Corrected feature-only and joint five-seed Macro-F1 means](online-experiments/figure_macro_f1.svg)

![Joint feature-reduction comparison](online-experiments/figure_feature_reduction.svg)

The corrected joint data are in [the 20-run CSV](COMP1818_EvoNIDS_Submission/results/protocol_runs/20261116T151402Z_full_joint/optimisers/runs.csv), [run summary](COMP1818_EvoNIDS_Submission/results/protocol_runs/20261116T151402Z_full_joint/optimisers/summary.csv), [paired statistics](COMP1818_EvoNIDS_Submission/results/statistical_analysis/paired_joint_comparison.csv) and [execution manifest](COMP1818_EvoNIDS_Submission/results/protocol_runs/20261116T151402Z_full_joint/manifest.json). The initial historical GA-leading results in `results/final_summary.csv` belong to a **different earlier study**; the mistakenly joint-labelled 16 November 10:07 run was actually feature-only and is **excluded** from joint HPO evidence.

The [optional HTML dashboard](online-experiments/index.html) is also included in the repository. GitHub Pages publication at https://francescoguerriero.github.io/COMP1818_EvoNIDS_with_React/ needs the repository owner to enable Settings → Pages → GitHub Actions. The SVG figures and CSVs above remain readable without Pages.

## For assessors

1. Read the [LaTeX PDF](COMP1818_EvoNIDS_Submission/report/latex/COMP1818_EvoNIDS_LaTeX/main.pdf) and its [figure provenance instructions](COMP1818_EvoNIDS_Submission/report/latex/COMP1818_EvoNIDS_LaTeX/README.md).
2. Inspect [the full experiment index](COMP1818_EvoNIDS_Submission/results/README.md) and original seed-level CSVs.
3. Run [Windows CI verification](https://github.com/FrancescoGuerriero/COMP1818_EvoNIDS_with_React/actions/workflows/evonids-windows-reproducibility.yml) (Actions → Run workflow) to check code, synthetic replay, published statistics and React build without raw benchmark data.
4. Use [full reproduction instructions](COMP1818_EvoNIDS_Submission/docs/REPRODUCTION.md) if independently rerunning official UNSW-NB15 optimisations with the separately downloaded dataset.

This project **does not host the original benchmark-trained GA model**; any synthetic `.joblib` in the smoke-test folders is for integration testing, not a claimed UNSW-NB15 benchmark classifier.
