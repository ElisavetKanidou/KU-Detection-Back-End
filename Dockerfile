FROM python:3.11-bullseye
COPY . /.
RUN pip install -r /requirements.txt
EXPOSE 5000
CMD ["python", "main.py"]