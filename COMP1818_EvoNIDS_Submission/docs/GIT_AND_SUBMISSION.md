# EvoNIDS — GitHub, LaTeX and submission checklist

## Canonical paths

Repository root: `COMP1818_EvoNIDS_with_React/`

Package root: `COMP1818_EvoNIDS_with_React/COMP1818_EvoNIDS_Submission/`

**Canonical LaTeX source:** `COMP1818_EvoNIDS_Submission/report/latex/COMP1818_EvoNIDS_LaTeX/main.tex`

The repository also contains a duplicate historical extracted archive in `report/COMP1818_EvoNIDS_LaTeX_Full_Four_Page_Project/` and a ZIP. They are not the preferred editable source. The compiled `main.pdf` under canonical LaTeX source is the current report variant. **Do not mistakenly compile `main.tex` from the package root or `report/latex/`; first enter the nested directory containing `main.tex`.**

## VS Code / Git Bash checks

From repository root:

```bash
git status -sb
git fetch origin
git log -1 --oneline
cd COMP1818_EvoNIDS_Submission
python -m pytest -q research/tests prototype/tests
python tools/check_repository_evidence.py
cd frontend && npm ci && npm run build
```

Python 3.12 and Node.js 22 are the versions used by the hosted Windows workflow. For local Python dependencies, first activate the project's `.venv` and run `python -m pip install -r requirements.txt`.

## Build the LaTeX report

```bash
cd COMP1818_EvoNIDS_Submission/report/latex/COMP1818_EvoNIDS_LaTeX
python -m pip install matplotlib
python figures/generate_figures.py
pdflatex -interaction=nonstopmode -halt-on-error main.tex
biber main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

When using the command above, run `cd` from the **repository root**. Windows needs a LaTeX distribution that provides both `pdflatex` and `biber` on PATH. Check the compiled PDF, figure captions, in-text references and four main-text pages plus references on the fifth. The report is an **adaptation** of the template example, not a verified reproduction of an unavailable institutional style package.

## Stage, commit and push without destroying evidence

```bash
cd ~/CourseWorks/Comp1818/COMP1818_EvoNIDS_with_React
git status --short
git diff --check
git diff --stat
git add -A
git diff --cached --stat
git diff --cached --name-only
```

**Inspect staged changes before committing**, especially deletions, duplicated LaTeX sources and generated files. Do not upload `.venv/`, `node_modules/`, raw UNSW-NB15 dataset partitions, credentials, `.env`, compiled LaTeX intermediates or untrusted model binaries. The source repo intentionally retains earlier research results; do not delete or overwrite them to make summaries appear consistent.

```bash
git commit -m "Update EvoNIDS documentation and submission evidence"
git push origin main
git fetch origin
git status -sb
git rev-parse HEAD
git rev-parse origin/main
```

The two SHAs should match after a successful push, and the working tree should be clean. An `Everything up-to-date` push message means **no unpushed commit**, not necessarily that local modified/untracked files are committed. If `git pull` would overwrite work, stop and commit or safely stash it first.

## Lecturer verification and online evidence

[Public root README](../../README.md) · [Online results and graphs](ONLINE_EXPERIMENTS.md) · [Experiment records](../results/README.md) · [Windows verification workflow](https://github.com/FrancescoGuerriero/COMP1818_EvoNIDS_with_React/actions/workflows/evonids-windows-reproducibility.yml).

GitHub Actions checks tests, synthetic replay, synthetic joint-mode exercise, source CSV statistics and React production compilation. The full official five-seed experiment is **not** rerun in CI. GitHub Pages requires the owner to enable Pages in Settings; charts in README work without Pages. The original full-data trained model is not publicly hosted.

Before submitting, check Moodle's report format, citation and AI-use rules. Do not assume the HTML evidence viewer replaces the formal submitted PDF.
