FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
EXPOSE 8501

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port 8000 & streamlit run frontend/streamlit_app.py --server.address 0.0.0.0"]