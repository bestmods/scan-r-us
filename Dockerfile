FROM debian:latest

WORKDIR /app

# Update packages.
RUN apt update
RUN apt upgrade -y

# Install base packages we'll need.
RUN apt install -y wget tar

# Install Python3.
RUN apt install -y python3-full python3-pip

# Install Postgres driver.
RUN apt install -y libpq-dev

# Install Firefox-ESR.
RUN apt install -y firefox-esr

# Retrieve geckodriver.
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz

# Extract new file.
RUN tar -xzvf geckodriver-v0.34.0-linux64.tar.gz

# Move 'geckodriver' to /usr/bin.
RUN mv geckodriver /usr/bin/

# Remove archive.
RUN rm -f geckodriver-v0.34.0-linux64.tar.gz

# Add group and user.
ARG GROUPID
ARG USERID

RUN addgroup --system --gid $GROUPID app
RUN adduser --system --uid $USERID app

# Copy over requirements and install them using PIP3.
COPY --chown=app:app requirements.txt .

# Install needed packages.
RUN pip3 install -r requirements.txt --break-system-packages

# Copy over source c ode.
COPY --chown=app:app src ./src

# Copy settings.
COPY --chown=app:app settings.json .

CMD [ "python3", "src/main.py" ]