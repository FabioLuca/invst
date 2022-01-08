FROM python:3

LABEL maintainer="pantano@gmail.com"

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set env variables for Cloud Run
ENV PORT 8080
ENV HOST 0.0.0.0

# Open port 5000
EXPOSE 8080:8080

# Run the application:
# CMD [ "python", "-m" , "automation.run_server"]
CMD [ "python" , "app.py"]