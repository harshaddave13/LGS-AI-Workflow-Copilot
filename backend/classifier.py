from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


MODEL_PATH = "models/lgs-requirement-classifier"


tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_PATH
)

model.eval()


def classify_requirement(text: str):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():

        outputs = model(**inputs)

        probabilities = torch.softmax(
            outputs.logits,
            dim=1
        )

        predicted_id = torch.argmax(
            probabilities,
            dim=1
        ).item()

        confidence = probabilities[0][
            predicted_id
        ].item()

    label = model.config.id2label[
        predicted_id
    ]

    return {
        "label": label,
        "confidence": confidence
    }