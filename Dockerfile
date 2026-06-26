FROM python:3.10

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0

# Dossier de travail
WORKDIR /app

# Dépendances Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copie du projet
COPY . .
RUN pip install --upgrade pip
ENV PIP_NO_CACHE_DIR=1

# Port FastAPI
EXPOSE 8000

# Lancement du serveur
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]