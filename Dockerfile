FROM python:3

LABEL maintainer="pantano@gmail.com"

EXPOSE 8080

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run the application:
CMD [ "python", "-m" , "automation.run_server"]