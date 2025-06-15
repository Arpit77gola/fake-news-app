from transformers import (
    BertTokenizer, BertForSequenceClassification,
    RobertaTokenizer, RobertaForSequenceClassification,
    DistilBertTokenizer, DistilBertForSequenceClassification,
    XLNetTokenizer, XLNetForSequenceClassification
)
import torch
import torch.nn.functional as F

# Load models and tokenizers once
MODEL_CACHE = {}

def load_model_and_tokenizer(model_name):
    if model_name == "BERT":
        model = BertForSequenceClassification.from_pretrained("bert-base-uncased")
        tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    elif model_name == "RoBERTa":
        model = RobertaForSequenceClassification.from_pretrained("roberta-base")
        tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
    elif model_name == "DistilBERT":
        model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased")
        tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    elif model_name == "XLNet":
        model = XLNetForSequenceClassification.from_pretrained("xlnet-base-cased")
        tokenizer = XLNetTokenizer.from_pretrained("xlnet-base-cased")
    else:
        raise ValueError(f"Unknown model: {model_name}")

    model.eval()
    return model, tokenizer

def predict_with_model(text, model_name):
    if model_name not in MODEL_CACHE:
        MODEL_CACHE[model_name] = load_model_and_tokenizer(model_name)

    model, tokenizer = MODEL_CACHE[model_name]
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=1)
        pred = torch.argmax(probs, dim=1).item()
        confidence = probs[0][pred].item() * 100

    label = "Real" if pred == 1 else "Fake"
    return label, round(confidence, 2)
