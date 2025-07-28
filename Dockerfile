FROM --platform=linux/amd64 python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY process_pdfs.py .
# RUN mkdir -p input output
CMD ["python", "process_pdfs.py"]