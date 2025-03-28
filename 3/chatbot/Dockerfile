FROM python:3.12.4

WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY __init__.py .
COPY controllers/*.py ./controllers/
COPY services/*.py ./services/

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["flask", "--app", "main", "run", "--host=0.0.0.0", "--port=5000", "--debug"]

# to build the image (from root directory)
#
# docker build --no-cache --pull --rm -f Dockerfile -t agsalguero/chatbot:latest "app"
#
# to push the image to Docker Hub
#
# docker push agsalguero/chatbot:latest
#
# to run the container for the first time
#
# docker run --name chatbot -p 5000:5000 agsalguero/chatbot:latest
#
# or go to the directory where the docker-compose.yml file is located and run
#
# docker-compose up
#
# or right click on the docker-compose.yaml file in Visual Studio Code and select Compose Up
#
# to run the container subsequent times
#
# docker start flask-app
#
# to attach a terminal to the running container
#
# docker exec -it flask-app bash
# 
# to stop the container
#
# docker stop flask-app
#
# to remove the container
#
# docker rm flask-app