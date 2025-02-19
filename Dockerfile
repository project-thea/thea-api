FROM python:3.11.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt
COPY . /app/

# Install cron
RUN apt-get update && apt-get -y install cron

# Copy crontab file to the cron.d directory
COPY scripts/crontab /etc/cron.d/process-locations

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/process-locations

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Apply cron job
RUN crontab /etc/cron.d/process-locations
