# ./Dockerfile

# Usa una imagen base de Python delgada
FROM python:3.11-slim

# Instala dependencias del sistema operativo necesarias para Tesseract y Poppler
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia solo el archivo de requerimientos para aprovechar el cache de Docker
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto en el que correrá Gunicorn
EXPOSE 8080

# Comando para iniciar la aplicación con Gunicorn (servidor de producción)
# app:server -> Busca la variable 'server' en el archivo 'app.py'
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "app:server"]