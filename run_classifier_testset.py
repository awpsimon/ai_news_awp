"""
Evaluate the classifier from diff_classifier_test.py against resources/testset.xlsx.

For each row the classifier is run four times:
  1. headline only
  2. headline + first 1000 chars of Body
  3. headline + first 2000 chars of Body
  4. headline + first 5000 chars of Body

Output columns per variant (suffix _headline / _1000 / _2000 / _5000):
  *_label   – top-1 label assigned by the classifier
  *_score   – confidence score for that label (or "forced" for keyword-matched invitations)
  *_time_s  – wall-clock seconds the classify() call took

Results are saved to resources/testset_results.csv
"""

import sys
import os
import time

import pandas as pd

# ---------------------------------------------------------------------------
# Bootstrap: make sure we run from the project root so relative imports work
# ---------------------------------------------------------------------------
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ---------------------------------------------------------------------------
# Import the classifier (initialises the model and DB connections once)
# ---------------------------------------------------------------------------
from tests.diff_classifier_test import classify  # noqa: E402

# ---------------------------------------------------------------------------
# Load the test set
# ---------------------------------------------------------------------------
TESTSET_PATH = os.path.join(project_root, "resources", "testset.xlsx")
OUTPUT_PATH = os.path.join(project_root, "resources", "testset_results.csv")

df = pd.read_excel(TESTSET_PATH)
print(f"Loaded {len(df)} rows from {TESTSET_PATH}")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
VARIANTS = {
    "headline": None,   # None → headline only
    "100":       100,
    "150":       150,
    "200":       200,
    "500":       500
}


def clean_text(text: str) -> str:
    import re
    text = re.sub(r'\r\n|\r', '\n', text)       # normalise line endings
    text = re.sub(r'\n{3,}', '\n\n', text)       # collapse excess blank lines
    text = re.sub(r'[^\S\n]+', ' ', text)        # collapse inline whitespace
    return text.strip()


def build_text(headline: str, body: str | None, limit: int | None) -> str:
    headline = str(headline) if headline is not None else ""
    if limit is None or not body or str(body).strip() == "":
        return clean_text(headline)
    body_snippet = str(body)[:limit]
    return clean_text(f"{headline}\n\n{body_snippet}")


def run_classify(text: str) -> tuple[str, str | float, float]:
    """Returns (label, score, elapsed_seconds)."""
    start = time.perf_counter()
    result = classify(text, details=True)
    elapsed = time.perf_counter() - start

    if isinstance(result, dict):
        labels = result.get("labels")
        scores = result.get("scores")
        # details=True returns labels as a list or forced string
        if isinstance(labels, list):
            label = labels[0]
            score = scores[0] if isinstance(scores, (list, tuple)) else scores
        else:
            # forced invitation label
            label = str(labels)
            score = scores  # "forced"
    else:
        label = str(result)
        score = None

    return label, score, elapsed


# ---------------------------------------------------------------------------
# Main evaluation loop
# ---------------------------------------------------------------------------
results = []

for idx, row in df.iterrows():
    headline = row.get("Headline", "")
    body = row.get("Body", "")
    manual_label = row.get("Label", "")
    lang = row.get("Lang", "")

    row_result = {
        "Headline": str(headline).replace("\n", " ").replace("\r", ""),
        "Lang": lang,
        "Manual_Label": manual_label,
    }

    for suffix, limit in VARIANTS.items():
        text = build_text(headline, body, limit)
        print(f"  [{idx+1}/{len(df)}] variant={suffix} ...", end=" ", flush=True)
        label, score, elapsed = run_classify(text)
        print(f"{label[:40]!r}  score={score}  t={elapsed:.2f}s")

        row_result[f"{suffix}_label"] = label
        row_result[f"{suffix}_score"] = round(score, 4) if isinstance(score, float) else score
        row_result[f"{suffix}_time_s"] = round(elapsed, 3)

    row_result["label_mismatch"] = row_result["headline_label"] != manual_label
    results.append(row_result)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
out_df = pd.DataFrame(results)
out_df.to_csv(OUTPUT_PATH, index=False, quoting=1)  # csv.QUOTE_ALL
print(f"\nSaved results to {OUTPUT_PATH}")
