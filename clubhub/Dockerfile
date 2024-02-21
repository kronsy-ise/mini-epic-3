# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

WORKDIR /clubhub

# Add the current directory contents into the container at /clubhub
ADD . /clubhub

# Install PostgreSQL development packages
RUN apt-get update && apt-get install -y libpq-dev gcc

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Remove unnecessary packages after installing requirements
RUN apt-get autoremove -y gcc

# Run app.py when the container launches
CMD ["python", "main.py"]