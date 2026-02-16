import os
import requests
from shiny import App, render, ui, reactive
from PIL import Image

# --- CONFIGURATION ---
# On récupère l'URL du backend définie dans le docker-compose
# Par défaut http://backend:8000 car c'est le nom du service Docker
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"),
        ui.tags.script(src="https://unpkg.com/panzoom@9.4.0/dist/panzoom.min.js"),
        ui.tags.style("""
            .main-title { text-align: center; font-weight: bold; font-size: 2.5rem; margin: 20px 0; }
            .image-container { width: 100%; height: 650px; overflow: hidden; background: #f0f0f0; border: 1px solid #ccc; cursor: grab; }
            #image_display img { max-width: 100%; height: auto; transform-origin: 0 0; }
            .btn-center-container { display: flex; justify-content: center; margin-top: 20px; }
            .label-q { color: red; font-weight: bold; margin-bottom: 5px; display: block; }
            .label-r { color: green; font-weight: bold; margin-bottom: 5px; display: block; margin-top: 10px; }
            .field-box { margin-bottom: 20px; padding: 10px; border: 1px solid #eee; border-radius: 5px; }
            .footer { text-align: center; padding: 25px; margin-top: 40px; border-top: 1px solid #e0e0e0; background-color: #f9f9f9; color: #444; width: 100%; }
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
    ui.div("Developed by Mahmoud Tourki", class_="footer")
)

def server(input, output, session):
    results_data = reactive.Value([])

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
        if not file_infos: return

        with ui.Progress(min=1, max=10) as p:
            p.set(2, message="Envoi au cerveau IA...")
            
            # Préparation du fichier pour l'envoi API
            file_path = file_infos[0]["datapath"]
            with open(file_path, "rb") as f:
                files = {"file": (file_infos[0]["name"], f, file_infos[0]["type"])}
                
                try:
                    # Appel de l'API Backend
                    response = requests.post(f"{BACKEND_URL}/analyze", files=files)
                    
                    if response.status_code == 200:
                        p.set(8, message="Traitement des résultats...")
                        data = response.json().get("data", [])
                        results_data.set(data)
                        p.set(10, message="Analyse terminée !")
                    else:
                        print(f"Erreur API: {response.text}")
                except Exception as e:
                    print(f"Erreur de connexion au backend: {e}")

    @output
    @render.ui
    def dynamic_form():
        data = results_data.get()
        if not data: return ui.p("En attente d'analyse IA...")

        form_items = []
        for idx, item in enumerate(data):
            form_items.append(
                ui.div(
                    ui.span("Question", class_="label-q"),
                    ui.div(ui.strong(item['question'] if item['question'] else "Champ détecté")),
                    ui.span("Réponse", class_="label-r"),
                    ui.input_text(f"field_{idx}", "", value=item['answer']),
                    class_="field-box"
                )
            )
        return ui.div(*form_items)

app = App(app_ui, server)