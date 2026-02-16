import numpy as np
import torch
import pytesseract
import os
import platform
from PIL import Image
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from shiny import App, render, ui, reactive

# --- 1. PATCH DE COMPATIBILITÉ NUMPY ---
if not hasattr(np, "unicode_"): np.unicode_ = np.str_
if not hasattr(np, "string_"): np.string_ = np.bytes_
if not hasattr(np, "bool_"): np.bool_ = bool
if not hasattr(np, "float_"): np.float_ = np.float64
if not hasattr(np, "int_"): np.int_ = np.int64

# --- 2. RESSOURCES & CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "Model_with_nms_kyc")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def load_resources():
    if not os.path.exists(MODEL_PATH):
        print(f"ERREUR : Dossier modele introuvable à {MODEL_PATH}")
        return None, None
    try:
        processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
        model = LayoutLMv3ForTokenClassification.from_pretrained(MODEL_PATH).to(device)
        model.eval()
        return processor, model
    except Exception as e:
        print(f"Erreur de chargement des ressources : {e}")
        return None, None

PROCESSOR, MODEL = load_resources()

# --- 3. INTERFACE UTILISATEUR (UI) ---
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"),
        ui.tags.script(src="https://unpkg.com/panzoom@9.4.0/dist/panzoom.min.js"),
        ui.tags.style("""
            .main-title { text-align: center; font-weight: bold; font-size: 2.5rem; margin: 20px 0; }
            .image-container { width: 100%; height: 650px; overflow: hidden; background: #f0f0f0; border: 1px solid #ccc; cursor: grab; }
            #image_display img { max-width: 100%; height: auto; transform-origin: 0 0; }
            .btn-center-container { display: flex; justify-content: center; margin-top: 20px; }
            .btn-analyse { padding: 15px 30px; font-size: 1.2rem; font-weight: bold; }
            .label-q { color: red; font-weight: bold; margin-bottom: 5px; display: block; }
            .label-r { color: green; font-weight: bold; margin-bottom: 5px; display: block; margin-top: 10px; }
            .field-box { margin-bottom: 20px; padding: 10px; border: 1px solid #eee; border-radius: 5px; }
            .footer { text-align: center; padding: 25px; margin-top: 40px; border-top: 1px solid #e0e0e0; background-color: #f9f9f9; color: #444; width: 100%; }
            .footer-links { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }
            .footer-links a { color: #0077b5; text-decoration: none; font-weight: 500; display: flex; align-items: center; }
            .footer-links i { margin-right: 8px; font-size: 1.2rem; }
        """)
    ),
    ui.div("FORM DIGITIZER KYC (Know Your Customer)", class_="main-title"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("📁 Document"),
            ui.input_file("file", "Charger l'image du formulaire", accept=[".png", ".jpg", ".jpeg"]),
        ),
        ui.layout_column_wrap(
            ui.div(
                ui.card(
                    ui.div(ui.output_image("image_display"), id="zoom_container", class_="image-container"),
                    ui.tags.script("""
                        setInterval(function() {
                            var img = document.querySelector('#image_display img');
                            if (img && !img.dataset.panzoomApplied) {
                                panzoom(img, { maxZoom: 5, minZoom: 0.5 });
                                img.dataset.panzoomApplied = "true";
                            }
                        }, 1000);
                    """),
                    full_screen=True
                ),
                ui.div(ui.input_action_button("process", "Lancer l'Analyse IA", class_="btn-primary btn-analyse"), class_="btn-center-container")
            ),
            ui.card(
                ui.card_header("📝 Champs Extraits"),
                ui.output_ui("dynamic_form")
            ),
            width=1/2
        )
    ),
    ui.div(
        ui.div("Developed by Mahmoud Tourki", style="font-weight: bold; margin-bottom: 10px;"),
        ui.div(
            ui.tags.a(
                ui.tags.i(class_="fa-solid fa-envelope"), 
                "mahmud.tourki24@gmail.com", 
                href="mailto:mahmud.tourki24@gmail.com"
            ),
            ui.tags.a(
                ui.tags.i(class_="fa-brands fa-linkedin"), 
                "MAHMOUD TOURKI", 
                href="https://www.linkedin.com/in/mahmoud-tourki-b228b9147/", 
                target="_blank"
            ),
            class_="footer-links"
        ),
        class_="footer"
    )
)

# (Le reste du serveur est identique à ton code précédent)
def server(input, output, session):
    results_lines = reactive.Value([])

    @output
    @render.image
    def image_display():
        file_infos = input.file()
        if not file_infos: return None
        return {"src": file_infos[0]["datapath"], "width": "100%"}

    @reactive.Effect
    @reactive.event(input.process)
    def run_inference():
        file_infos = input.file()
        if not file_infos or not PROCESSOR or not MODEL: return

        with ui.Progress(min=1, max=10) as p:
            p.set(2, message="Extraction OCR...")
            img = Image.open(file_infos[0]["datapath"]).convert("RGB")
            w_orig, h_orig = img.size
            
            ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            words, boxes = [], []
            for i, text in enumerate(ocr_data['text']):
                if text.strip() != "":
                    words.append(text)
                    x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
                    boxes.append([int(1000*(x/w_orig)), int(1000*(y/h_orig)), int(1000*((x+w)/w_orig)), int(1000*((y+h)/h_orig))])

            p.set(5, message="Analyse LayoutLMv3...")
            encoding = PROCESSOR(img, text=words, boxes=boxes, return_tensors="pt", truncation=True, padding="max_length")
            for k, v in encoding.items(): encoding[k] = v.to(device)

            with torch.no_grad():
                outputs = MODEL(**encoding)

            predictions = outputs.logits.argmax(-1).squeeze().tolist()
            input_ids = encoding['input_ids'].squeeze().tolist()
            out_boxes = encoding['bbox'].squeeze().tolist()
            id2label = MODEL.config.id2label

            entities = []
            for i in range(len(input_ids)):
                label = id2label[predictions[i]]
                if label == "O" or input_ids[i] in [PROCESSOR.tokenizer.cls_token_id, PROCESSOR.tokenizer.sep_token_id]:
                    continue
                
                word_part = PROCESSOR.tokenizer.decode([input_ids[i]]).strip()
                raw_token = PROCESSOR.tokenizer.convert_ids_to_tokens([input_ids[i]])[0]
                
                if entities and not raw_token.startswith('Ġ') and entities[-1]['label'] == label.split("-")[-1]:
                    entities[-1]['text'] += word_part
                else:
                    entities.append({"text": word_part, "label": label.split("-")[-1], "y": out_boxes[i][1], "x": out_boxes[i][0]})

            p.set(8, message="Reconstruction des lignes...")
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
            
            results_lines.set(lines)
            p.set(10, message="Analyse terminée !")

    @output
    @render.ui
    def dynamic_form():
        lines = results_lines.get()
        if not lines: return ui.p("En attente d'analyse IA...")

        form_items = []
        for idx, line in enumerate(lines):
            question = " ".join([e['text'] for e in line if e['label'] == "QUESTION"]).strip()
            answer = " ".join([e['text'] for e in line if e['label'] == "ANSWER"]).strip()

            if question or answer:
                form_items.append(
                    ui.div(
                        ui.span("Questions", class_="label-q"),
                        ui.div(ui.strong(question if question else "Champ détecté")),
                        ui.span("Réponses", class_="label-r"),
                        ui.input_text(f"field_{idx}", "", value=answer),
                        class_="field-box"
                    )
                )
        return ui.div(*form_items)

app = App(app_ui, server)