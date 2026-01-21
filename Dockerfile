# Usa uma imagem leve do Python
FROM python:3.9-slim

# Evita criação de ficheiros .pyc e mostra logs imediatamente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define a pasta de trabalho
WORKDIR /app

# Instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código para dentro do container
COPY . .

# COMANDO DE ARRANQUE CORRIGIDO PARA O TEU run.py
CMD ["python", "run.py"]