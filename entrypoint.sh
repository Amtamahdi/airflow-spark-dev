#!/bin/bash

# Attendre que PostgreSQL soit prêt
while ! nc -z postgres 5432; do
    echo "En attente de PostgreSQL..."
    sleep 1
done

# Initialiser Airflow si nécessaire
if [ ! -f "/opt/airflow/airflow-webserver.pid" ]; then
    airflow db init
    
    airflow users create \
        --username admin \
        --firstname admin \
        --lastname admin \
        --role Admin \
        --email admin@example.com \
        --password admin
fi

# Exécuter la commande passée en argument
exec "$@"