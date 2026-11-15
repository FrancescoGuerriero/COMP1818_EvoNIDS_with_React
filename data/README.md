# UNSW-NB15 data

Download the official UNSW-NB15 *training* and *testing* CSV partitions from
https://research.unsw.edu.au/projects/unsw-nb15-dataset

Put the files at:
- `data/raw/UNSW_NB15_training-set.csv` (175,341 records)
- `data/raw/UNSW_NB15_testing-set.csv` (82,332 records)

The CSVs are not committed to Git. The Windows GitHub Actions **full** workflow
uses a documented public mirror of the two partitions, records SHA-256 hashes,
and checks row counts. Compare those hashes with the official originals before
claiming exact dataset equivalence. Research runs do not use test data for search.