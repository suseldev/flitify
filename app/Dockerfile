FROM python:3.13.3

WORKDIR /app
COPY ./app .
RUN pip install --no-cache-dir -r requirements.txt
# Generate keys
RUN python3 crypto/utils/rsakeyutils.py .
CMD ["python3", "server_main.py"]
