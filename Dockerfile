FROM python:3.8

WORKDIR /app

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt update
RUN apt install tesseract-ocr -y
#/usr/share/tesseract-ocr/4.00/tessdata

COPY . .

CMD python -u /app/main.py