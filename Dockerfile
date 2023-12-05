FROM python:3.8.10

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./app/index.html /code
COPY ./app /code/app


CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--reload", "--port", "8000"]

