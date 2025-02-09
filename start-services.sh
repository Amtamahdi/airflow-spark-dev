#!/bin/bash

# Attendre que PostgreSQL soit prêt
while ! nc -z postgres 5432; do
    echo "En attente de PostgreSQL..."
    sleep 1
done

# Initialiser la base de données Airflow si nécessaire
airflow db init

# Créer un compte admin si nécessaire
if ! airflow users list | grep -q 'admin'; then
    airflow users create \
        --username admin \
        --firstname admin \
        --lastname admin \
        --role Admin \
        --email admin@example.com \
        --password admin
fi

# Démarrer le webserver
exec airflow webserver