# Utilisation d'une image Python légère
FROM python:3.9-slim

# 1. Installation des dépendances système
# Correction : libgl1 remplace libgl1-mesa-glx pour les distributions Debian récentes
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Définition du répertoire de travail
WORKDIR /app

# 3. Installation des dépendances Python
# On utilise --index-url pour le CPU si tu n'as pas besoin de GPU (gain de place énorme)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copie du code source
COPY . .

# 5. Exposition du port pour l'API FastAPI
EXPOSE 8000

# 6. Lancement de l'API avec Uvicorn
# On utilise main:app car ton fichier s'appelle main.py et ton instance FastAPI s'appelle app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]