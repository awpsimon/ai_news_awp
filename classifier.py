from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer, pipeline
import logging
from db_pool import pool
import pandas as pd

# Load classifier
# classifier = pipeline("zero-shot-classification", model="knowledgator/comprehend_it-base")
tokenizer = AutoTokenizer.from_pretrained("laiyer/deberta-v3-base-zeroshot-v1-onnx")
model = ORTModelForSequenceClassification.from_pretrained("laiyer/deberta-v3-base-zeroshot-v1-onnx")
classifier = pipeline(
    task="zero-shot-classification",
    model=model,
    tokenizer=tokenizer,
)
logging.info("classifier ready")

# Load labels
# awp
db = pool.get_connection()
sql_stmt = "SELECT * FROM ai_texts.topics;"
label_overview = pd.read_sql(sql_stmt, db)
# pubt
sql_stmt = ("SELECT code AS pubt_code, label, bw2_code as subject_codes, prompt_id_de, prompt_id_fr, "
            "prompt_id_flash_de, prompt_id_flash_fr "
            "FROM wires.pubt_codes WHERE NOT "
            "label IS NULL "
            "ORDER BY length(bw2_code) DESC, ord DESC, code DESC;")
pubt_labels = pd.read_sql(sql_stmt, db)
db.close()

# Word collections for pre-check
INVITATION_KEYWORDS = [
    'invitation', 'invite', 'reminder',
    'save the date', 'conference call', 'webcast',
    'announces date',
    'dial-in', 'register', 'präsentation', 'einladung',
    'to publish', 'to release'
]

AGM_KEYWORDS = [
    'annual general meeting', 'generalversammlung',
    ' agm', 'agm ', ' gv', 'gv '
]

# Length of additional text
ADDITIONAL_TEXT_LENGTH = 300


def reduce_text(text: str) -> str:
    import re
    text = re.sub(r'\r\n|\r', '\n', text)  # normalise line endings
    text = re.sub(r'\n{3,}', '\n\n', text)  # collapse excess blank lines
    text = re.sub(r'[^\S\n]+', ' ', text)  # collapse inline whitespace
    return text.strip()


def classify(text, additional_text="", details=True):
    # First check for invitation signals
    text_lower = text.lower()
    forced_label = None
    if any(kw in text_lower for kw in AGM_KEYWORDS):
        # Force the AGM label
        forced_label = label_overview[label_overview['label'].str.contains('shareholders meeting', case=False)]
    elif any(kw in text_lower for kw in INVITATION_KEYWORDS):
        # Force the invitation label
        forced_label = label_overview[label_overview['label'].str.contains('invitation', case=False)]
    if forced_label is not None:
        forced_label = forced_label.iloc[0]['label']
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
    # Run automated classifier
    candidate_labels = label_overview['label'].tolist()
    # Remove option invitations for likely AGM-releases
    if any(kw in text_lower for kw in AGM_KEYWORDS):
        candidate_labels.remove("invitations and financial calendar")
    # Normalize all uppercase headline for better results
    if text.isupper():
        text = text.lower()
    text = reduce_text(text)
    labels = classifier(text, candidate_labels, multi_label=True)
    logging.info("Release %s classified as %s", text[:80], labels.get("labels")[0])
    # Rerun if confidence is too low
    if labels.get("scores")[0] < 0.5 and additional_text != "":
        additional_text = text + "\n\n" + reduce_text(str(additional_text))[:ADDITIONAL_TEXT_LENGTH]
        labels_new = classifier(additional_text, candidate_labels, multi_label=True)
        if labels_new.get("scores")[0] >= labels.get("scores")[0]:
            labels = labels_new
            logging.info("After rerun with more text Release %s classified as %s", text[:80], labels.get("labels")[0])

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


def get_pubt_classification(code):
    searchcode = code.split(" ")
    metadata = pubt_labels[pubt_labels['pubt_code'].isin(searchcode)]
    if len(metadata) > 0:
        result = {"label": metadata['label'].iloc[0],
                  "subject_codes": metadata['subject_codes'].iloc[0],
                  "prompt_id_de": metadata['prompt_id_de'].iloc[0],
                  "prompt_id_fr": metadata['prompt_id_fr'].iloc[0],
                  "prompt_id_flash_de": metadata['prompt_id_flash_de'].iloc[0],
                  "prompt_id_flash_fr": metadata['prompt_id_flash_fr'].iloc[0]}
    else:
        result = {"label": None,
                  "subject_codes": None,
                  "prompt_id_de": None,
                  "prompt_id_fr": None,
                  "prompt_id_flash_de": None,
                  "prompt_id_flash_fr": None}
    return result
