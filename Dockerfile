# Dockerfile
FROM python:3.10

WORKDIR /app

# Copy requirements separately to leverage Docker cache
COPY requirements.txt .
COPY init.sh .

RUN pip install -r requirements.txt

COPY api.py ./api.py
COPY credential.py ./credential.py
COPY fast_api.py ./fast_api.py
COPY scraper.py ./scraper.py
COPY setup.py ./setup.py
COPY celery_app.py ./celery_app.py
COPY services.py ./services.py
# Give permission to modify files inside the container
# RUN chmod -R 777 /app
# RUN chmod +x /app/init.sh

# Copy init.sh and set as executable

# Entrypoint to run the init.sh script
ENTRYPOINT ["sh", "/app/init.sh"]
# ENTRYPOINT [ "tail", "-f",  "/dev/null" ]
