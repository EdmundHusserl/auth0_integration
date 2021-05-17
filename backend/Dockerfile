FROM     python:3.7-slim
EXPOSE   5000
WORKDIR  /backend 
COPY     . .
RUN      apt update -y \
            && apt install gcc -y \
            && pip install -r ./requirements.txt 
ENV      FLASK_APP=src/api.py FLASK_ENV=development
CMD      ["flask", "run", "--host", "0.0.0.0"]