FROM python:3.9

WORKDIR /fastapi

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /fastapi

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]