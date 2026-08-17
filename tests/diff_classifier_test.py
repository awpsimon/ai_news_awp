from transformers import pipeline, AutoTokenizer
from optimum.onnxruntime import ORTModelForSequenceClassification
from timeit import default_timer as timer
import logging
from db_pool import pool
import pandas as pd

INVITATION_KEYWORDS = [
    'invitation', 'invite', 'reminder',
    'save the date', 'conference call', 'webcast',
    'dial-in', 'register', 'präsentation', 'einladung'
]

AGM_KEYWORDS = [
    'annual general meeting', 'generalversammlung'
]

# # Load the quantized model
# model = ORTModelForSequenceClassification.from_pretrained(
#     "richardr1126/roberta-base-zeroshot-v2.0-c-ONNX",
#     file_name="model_quantized.onnx"
# )
#
# tokenizer = AutoTokenizer.from_pretrained(
#     "richardr1126/roberta-base-zeroshot-v2.0-c-ONNX"
# )
#
# # Patch the model's forward method to handle token_type_ids
# original_forward = model.forward
#
#
# def patched_forward(input_ids=None, attention_mask=None, token_type_ids=None, **kwargs):
#     return original_forward(input_ids=input_ids, attention_mask=attention_mask, **kwargs)
#
#
# model.forward = patched_forward
#
# # Create zero-shot classification pipeline
# classifier = pipeline("zero-shot-classification",
#                       model=model,
#                       tokenizer=tokenizer,
#                       device=-1  # CPU inference
#                       )

# Use a pipeline as a high-level helper
# Load model directly
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer, pipeline

tokenizer = AutoTokenizer.from_pretrained("laiyer/deberta-v3-base-zeroshot-v1-onnx")
model = ORTModelForSequenceClassification.from_pretrained("laiyer/deberta-v3-base-zeroshot-v1-onnx")
classifier = pipeline(
    task="zero-shot-classification",
    model=model,
    tokenizer=tokenizer,
)

# tokenizer = AutoTokenizer.from_pretrained("MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
# model = ORTModelForSequenceClassification.from_pretrained("MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
# classifier = pipeline(
#     task="zero-shot-classification",
#     model=model,
#     tokenizer=tokenizer,
# )



# Load labels
# awp
db = pool.get_connection()
sql_stmt = "SELECT * FROM ai_texts.topics;"
label_overview = pd.read_sql(sql_stmt, db)
# label_overview.iloc[0]['label'] = 'Publication of financial results: actual earnings figures, revenue, profit or loss'
# label_overview.iloc[2]['label'] = 'Invitation to financial event, reminder or announcement of upcoming results presentation date'
# pubt
sql_stmt = ("SELECT code AS pubt_code, label, bw2_code as subject_codes, prompt_id_de, prompt_id_fr, "
            "prompt_id_flash_de, prompt_id_flash_fr "
            "FROM wires.pubt_codes WHERE NOT "
            "label IS NULL;")
pubt_labels = pd.read_sql(sql_stmt, db)
db.close()


def classify(text, details=True):
    text_lower = text.lower()
    inv_label = None
    if any(kw in text_lower for kw in INVITATION_KEYWORDS) and not any(kw in text_lower for kw in AGM_KEYWORDS):
        # Force the invitation label
        inv_label = label_overview[label_overview['label'].str.contains('invitation', case=False)]
    if inv_label is not None:
        forced_label = inv_label.iloc[0]['label']
        if details:
            return {"sequence": text, "labels": forced_label, "scores": "forced"}
        else:
            metadata = label_overview[label_overview['label'] == forced_label]
            result = {"label": forced_label,
                      "subject_codes": metadata['subject_codes'].iloc[0],
                      "prompt_id_de": metadata['prompt_id_de'].iloc[0],
                      "prompt_id_fr": metadata['prompt_id_fr'].iloc[0],
                      "prompt_id_flash_de": metadata['prompt_id_flash_de'].iloc[0],
                      "prompt_id_flash_fr": metadata['prompt_id_flash_fr'].iloc[0]}
            return result

    candidate_labels = label_overview['label'].tolist()
    labels = classifier(text, candidate_labels, multi_label=True)

    if details:
        return labels
    else:
        label = labels.get("labels")[0]
        metadata = label_overview[label_overview['label'] == label]
        result = {"label": label,
                  "subject_codes": metadata['subject_codes'].iloc[0],
                  "prompt_id_de": metadata['prompt_id_de'].iloc[0],
                  "prompt_id_fr": metadata['prompt_id_fr'].iloc[0],
                  "prompt_id_flash_de": metadata['prompt_id_flash_de'].iloc[0],
                  "prompt_id_flash_fr": metadata['prompt_id_flash_fr'].iloc[0]}
        return result


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

for headline in headlines:
    start = timer()
    print(classify(headline, True))
    end = timer()
    print(end - start)
