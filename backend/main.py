import os
import io
import torch
import pytesseract
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification

# --- PATCH NUMPY ---
if not hasattr(np, "int_"): np.int_ = np.int64

app = FastAPI()

# --- CONFIGURATION ---
MODEL_ID = "tourki24/kyc-layoutlmv3-digitizer"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

# Chargement du modèle
print(f"Chargement du modèle {MODEL_ID}...")
processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
model = LayoutLMv3ForTokenClassification.from_pretrained(MODEL_ID, ignore_mismatched_sizes=True).to(device)
model.eval()
id2label = model.config.id2label

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    w_orig, h_orig = img.size

    # OCR
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    words, boxes = [], []
    for i, text in enumerate(ocr_data['text']):
        if text.strip() != "":
            words.append(text)
            x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
            boxes.append([int(1000*(x/w_orig)), int(1000*(y/h_orig)), int(1000*((x+w)/w_orig)), int(1000*((y+h)/h_orig))])

    # Inférence IA
    encoding = processor(img, text=words, boxes=boxes, return_tensors="pt", truncation=True, padding="max_length")
    for k, v in encoding.items(): encoding[k] = v.to(device)
    
    with torch.no_grad():
        outputs = model(**encoding)

    predictions = outputs.logits.argmax(-1).squeeze().tolist()
    input_ids = encoding['input_ids'].squeeze().tolist()
    out_boxes = encoding['bbox'].squeeze().tolist()

    # Extraction des entités
    entities = []
    for i in range(len(input_ids)):
        label = id2label[predictions[i]]
        if label == "O" or input_ids[i] in [processor.tokenizer.cls_token_id, processor.tokenizer.sep_token_id, processor.tokenizer.pad_token_id]:
            continue
        
        word_part = processor.tokenizer.decode([input_ids[i]]).strip()
        raw_token = processor.tokenizer.convert_ids_to_tokens([input_ids[i]])[0]
        
        if entities and not raw_token.startswith('Ġ') and entities[-1]['label'] == label.split("-")[-1]:
            entities[-1]['text'] += word_part
        else:
            entities.append({"text": word_part, "label": label.split("-")[-1], "y": out_boxes[i][1], "x": out_boxes[i][0]})

    # Reconstruction des lignes
    lines = []
    if entities:
        entities.sort(key=lambda e: e['y'])
        current_line = [entities[0]]
        for i in range(1, len(entities)):
            if abs(entities[i]['y'] - current_line[-1]['y']) < 15:
                current_line.append(entities[i])
            else:
                lines.append(sorted(current_line, key=lambda e: e['x']))
                current_line = [entities[i]]
        lines.append(sorted(current_line, key=lambda e: e['x']))

    # Formatage final pour le frontend
    structured_results = []
    for line in lines:
        q = " ".join([e['text'] for e in line if e['label'] == "QUESTION"]).strip()
        a = " ".join([e['text'] for e in line if e['label'] == "ANSWER"]).strip()
        if q or a:
            structured_results.append({"question": q if q else "Champ détecté", "answer": a})

    return {"status": "success", "data": structured_results}