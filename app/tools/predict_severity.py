from typing import Any
from transformers import pipeline

NEEDLESTICK_KEYWORDS = {
    "needle",
    "needlestick",
    "lancet",
    "sharps",
    "puncture",
}

CLASS_LABELS = {
    "LABEL_0": "None (0 days)",
    "LABEL_1": "Minor (1-2 days)",
    "LABEL_2": "Moderate (3-7 days)",
    "LABEL_3": "Severe (8-28 days)",
    "LABEL_4": "Major (29+ days)",
}

_classifier = pipeline(
    "text-classification",
    model="stuSterfc/ohs-severity-classifier",
    top_k=None,
)


def detect_needlestick(narrative: str) -> bool:
    tokens = narrative.lower().split()
    return any(token.strip(".,;:") in NEEDLESTICK_KEYWORDS for token in tokens)


def detect_ambiguous_severity(predicted_class: int) -> bool:
    return predicted_class in [2, 3, 4]


def predict_severity(narrative: str) -> dict:
    needlestick_flag = detect_needlestick(narrative)

    raw: list[list[dict[str, Any]]] = _classifier(narrative)  # type: ignore[assignment]
    scores: list[dict[str, Any]] = raw[0]

    probabilities = {
        CLASS_LABELS[item["label"]]: round(item["score"], 4)
        for item in scores
    }

    top = max(scores, key=lambda x: x["score"])
    predicted_label = CLASS_LABELS[top["label"]]
    predicted_class = list(CLASS_LABELS.keys()).index(top["label"])

    return {
        "predicted_class": predicted_class,
        "predicted_label": predicted_label,
        "confidence": round(top["score"], 4),
        "probabilities": probabilities,
        "needlestick_flag": needlestick_flag,
        "ambiguous_severity_flag": detect_ambiguous_severity(predicted_class),
    }