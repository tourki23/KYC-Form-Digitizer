# Utilisation d'une image Python légère
FROM python:3.11-slim

# 1. Installation des dépendances système
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Définition du répertoire de travail
WORKDIR /app

# 3. Copie des dépendances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copie du code de l'application (On garde le nom original)
COPY kyc-app.py .

# 5. Copie du dossier modèle (Assure-toi qu'il est au même niveau que le Dockerfile)
COPY Model_with_nms_kyc/ ./Model_with_nms_kyc/

# 6. Exposition du port Shiny
EXPOSE 8050

# 7. Commande de lancement (Cible le bon fichier)
CMD ["shiny", "run", "--host", "0.0.0.0", "--port", "8050", "kyc-app.py"]