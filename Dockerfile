# Use an official Python runtime as a parent image
FROM python:3.9-slim

ENV FLASK_APP=flaskr
ENV FLASK_ENV=development
ENV TCP_IP=127.0.0.1
ENV TCP_PORT=10110

# Copy the current directory contents into the container at /app
COPY app /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]