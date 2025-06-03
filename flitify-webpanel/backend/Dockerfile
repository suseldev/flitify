FROM python:3.13.3

WORKDIR /flitify-webpanel/backend/
COPY ./flitify-webpanel/backend/ .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python3", "app.py"]
