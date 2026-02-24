FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dat2bmp.py add_image_to_dat.py .

# First argument is the script: dat2bmp.py or add_image_to_dat.py
ENTRYPOINT ["python", "-u"]
CMD ["dat2bmp.py", "/data", "-o", "/output"]
