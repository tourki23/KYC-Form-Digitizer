# Utilisation d'une image Python légère
FROM python:3.11-slim

# 1. Installation des dépendances système
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean

# 2. Définition du répertoire de travail
WORKDIR /app

# 3. Copie des dépendances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copie du code de l'application
COPY kyc-app.py ./app.py
# Note : Le modèle sera monté via un volume ou copié ici
# COPY Model_with_nms_kyc/ ./Model_with_nms_kyc/

# 5. Exposition du port Shiny
EXPOSE 8050

# 6. Commande de lancement
CMD ["shiny", "run", "--host", "0.0.0.0", "--port", "8050", "app.py"]