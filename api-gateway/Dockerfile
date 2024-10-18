FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

COPY ./main.py /app/main.py

RUN pip install httpx

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
