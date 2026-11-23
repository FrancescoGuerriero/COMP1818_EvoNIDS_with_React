# COMP-1818 EvoNIDS — Reproducible LaTeX report

This is an editable scientific-paper adaptation of the supplied coursework-template PDF, **not** the original style-file package (which was not available).

## Compile

```bash
python figures/generate_figures.py
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

The output `main.pdf` has **five A4 pages**: four for the report and one for references/reproducibility.

## Figure provenance

Both figures are generated directly by `matplotlib.pyplot.savefig()` in `figures/generate_figures.py`, reading these bundled CSV snapshots:

- `data/feature_only_summary.csv`, copied from `COMP1818_EvoNIDS_Submission/results/protocol_runs/20261115T183225Z_full/optimisers/summary.csv` in the [public source repository](https://github.com/FrancescoGuerriero/COMP1818_EvoNIDS_with_React).
- `data/corrected_joint_summary.csv`, copied from `COMP1818_EvoNIDS_Submission/results/protocol_runs/20261116T151402Z_full_joint/optimisers/summary.csv` in the same repository.

The previously invalid `20261116T100750Z_full_joint` output is excluded. Both plots depict aggregate results from the published experiment, not synthetic smoke-test data. Re-run the generator to update PNGs and rebuild the report. The bundled CSVs preserve the reported published summary values; individual seed-level observations and analysis code are available in the public repository.

## LaTeX semantics

- Equation: `\begin{equation}` with `\label{eq:fitness}`, referenced using `\eqref{eq:fitness}`.
- Tables: `\begin{table}` and `\begin{tabular}` with captions/labels, referenced using `\ref{tab:results}` and `\ref{tab:paired}`.
- Figures: `\begin{figure}` and `\includegraphics` with detailed captions/labels, referenced using `\ref{fig:performance}` and `\ref{fig:tradeoff}`.
- Author–date bibliography: BibLaTeX `\parencite` and `ref.bib`.

This report preserves the original EvoNIDS scientific content while repairing provenance and citation presentation. Verify course-specific submission rules before uploading.

## Latest report expansion

The four-page research body now includes discussion of the limits of five-seed aggregate plots, separation of figure reproduction from full model retraining, and why benchmark false-positive rates and feature-count reductions do not directly establish live-system efficiency. References remain on page five.
