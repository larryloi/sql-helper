FROM python:3.8

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ unixodbc-dev gnupg curl procps && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/debian/10/prod buster main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt -v

CMD ["python", "-u", "mssql_inventory/invoices_creator.py"]
