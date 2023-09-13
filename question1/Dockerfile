FROM --platform=linux/amd64 public.ecr.aws/docker/library/python:3.8.12-slim-buster

COPY requirements.txt  ./
RUN python -m pip install -r requirements.txt

COPY app.py  ./

# gradio specific deployment settings
EXPOSE 80
ENV GRADIO_SERVER_NAME="0.0.0.0"
CMD ["python3", "app.py"]