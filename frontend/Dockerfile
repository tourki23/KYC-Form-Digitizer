# Image Python légère
FROM python:3.9-slim

# 1. Définition du répertoire de travail
WORKDIR /app

# 2. Installation des dépendances (Shiny, requests, etc.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copie du code de l'interface Shine
COPY . .

# 4. Exposition du port Shiny (8080 par défaut pour éviter les conflits)
EXPOSE 8080

# 5. Commande pour lancer l'application Shine
CMD ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "8080"]