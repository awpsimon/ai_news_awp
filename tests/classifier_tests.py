import classifier
from timeit import default_timer as timer
import os
import sys
import time
import pandas as pd

headlines = ("Partners Group's&#160;Financial Results as of 31 December 2025",
             "Invitation to the Conference Call for Investors, Analysts and Media",
             "DORMAKABA Holding AG - dormakaba strengthens its hotel business in Australia through the acquisition of "
             "the operating business of Vintech",
             "DORMAKABA Holding AG - dormakaba stärkt Hotelgeschäft in Australien durch Akquisition des operativen "
             "Geschäfts von Vintech",
             "Avolta Ltd. - Avolta's FY 2025 Results Invitation ",
             "UBS reports net profit of USD 1.2bn in 4Q25 and USD 7.8bn in FY25; increases dividend by 22% YoY; "
             "confirms 2026 targets and sets ambitions for 2028 (Ad hoc announcement pursuant to Article 53 of the "
             "SIX Exchange Regulation Listing Rules)",
             "UBS Group AG - Media release (4q25 media release en)",
             "Reminder: Presentation of Leonteq's full-year 2025 results",
             "Basilea Pharmaceutica AG - Strong Cresemba® (isavuconazole) sales "
             "performance in Asia Pacific and China triggers milestone payment to Basilea",
             "Basilea Pharmaceutica Ltd, Allschwil (SIX: BSLN), a commercial-stage biopharmaceutical company "
             "committed to meeting the needs of patients with severe bacterial and fungal infections, announced today "
             "that the continued strong sales performance of the antifungal Cresemba(R) (isavuconazole), "
             "by its license partner Pfizer Inc. in the Asia Pacific region and China, exceeded the sales threshold "
             "triggering a USD 5 million milestone payment. David Veitch, Basilea's Chief Executive Officer, "
             "stated: \"We are pleased with the strong sales performance from our partner Pfizer for the Asia Pacific "
             "region, including China. This milestone payment reflects the significant and increasing demand for "
             "novel antifungal therapies and Cresemba's clinical value for patients facing life-threatening invasive "
             "mold infections in this region. We are grateful to our partner Pfizer for their ongoing commitment to "
             "making Cresemba available to patients in need.\"")

# for headline in headlines:
#     start = timer()
#     print(classifier.classify(headline, True))
#     end = timer()
#     print(end - start)


def run_classify(hl: str, text: str) -> tuple[str, str | float, float]:
    """Returns (label, score, elapsed_seconds)."""
    strt = time.perf_counter()
    result = classifier.classify(hl, text, details=True)
    elapsd = time.perf_counter() - strt

    if isinstance(result, dict):
        labels = result.get("labels")
        scores = result.get("scores")
        # details=True returns labels as a list or forced string
        if isinstance(labels, list):
            labl = labels[0]
            scre = scores[0] if isinstance(scores, (list, tuple)) else scores
        else:
            # forced invitation label
            labl = str(labels)
            scre = scores  # "forced"
    else:
        labl = str(result)
        scre = None

    return labl, scre, elapsd


# ---------------------------------------------------------------------------
# Bootstrap: make sure we run from the project root so relative imports work
# ---------------------------------------------------------------------------
project_root = "C:\\Automatisierungen\\ai_news_api"

# ---------------------------------------------------------------------------
# Load the test set
# ---------------------------------------------------------------------------
TESTSET_PATH = os.path.join(project_root, "resources", "testset.xlsx")
OUTPUT_PATH = os.path.join(project_root, "resources", "testset_results.csv")

df = pd.read_excel(TESTSET_PATH)
print(f"Loaded {len(df)} rows from {TESTSET_PATH}")

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

    label, score, elapsed = run_classify(headline, body)
    print(f"{label[:40]!r}  score={score}  t={elapsed:.2f}s")

    row_result[f"label"] = label
    row_result[f"score"] = round(score, 4) if isinstance(score, float) else score
    row_result[f"time_s"] = round(elapsed, 3)

    row_result["label_mismatch"] = row_result["label"] != manual_label
    results.append(row_result)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
out_df = pd.DataFrame(results)
out_df.to_csv(OUTPUT_PATH, index=False, quoting=1)  # csv.QUOTE_ALL
print(f"\nSaved results to {OUTPUT_PATH}")
