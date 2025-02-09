from pyspark.sql import SparkSession
import requests
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import logging
import sys

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_pokemon_data(start_id=1, end_id=100):
    """Récupère les données de l'API Pokemon"""
    logger.info(f"Début de la récupération des données Pokemon de {start_id} à {end_id}")
    pokemons = []
    for pokemon_id in range(start_id, end_id + 1):
        try:
            logger.info(f"Récupération du Pokemon {pokemon_id}")
            response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}')
            if response.status_code == 200:
                data = response.json()
                pokemon = {
                    'id': data['id'],
                    'name': data['name'],
                    'height': data['height'],
                    'weight': data['weight'],
                    'base_experience': data['base_experience'],
                    'type_1': data['types'][0]['type']['name'],
                    'type_2': data['types'][1]['type']['name'] if len(data['types']) > 1 else None
                }
                pokemons.append(pokemon)
            else:
                logger.warning(f"Erreur {response.status_code} pour Pokemon {pokemon_id}")
        except Exception as e:
            logger.error(f"Erreur pour Pokemon {pokemon_id}: {str(e)}")
    logger.info(f"Récupération terminée. {len(pokemons)} Pokemons récupérés")
    return pokemons

def create_table_if_not_exists(spark, url, properties):
    """Crée la table si elle n'existe pas"""
    try:
        spark.sql("""
        CREATE TABLE IF NOT EXISTS pokemon_data (
            id INT PRIMARY KEY,
            name STRING,
            height INT,
            weight INT,
            base_experience INT,
            type_1 STRING,
            type_2 STRING
        )
        """)
        logger.info("Table créée ou déjà existante")
    except Exception as e:
        logger.error(f"Erreur lors de la création de la table: {str(e)}")
        raise

def main():
    try:
        logger.info("Démarrage du job Spark")
        
        # Création de la session Spark
        spark = SparkSession.builder \
            .appName("PokemonETL") \
            .config("spark.jars", "/opt/airflow/postgresql-42.2.18.jar") \
            .getOrCreate()

        logger.info("Session Spark créée")

        # Récupération des données
        pokemon_data = get_pokemon_data()

        if not pokemon_data:
            logger.error("Aucune donnée Pokemon récupérée")
            sys.exit(1)

        # Définition du schéma
        schema = StructType([
            StructField("id", IntegerType(), False),
            StructField("name", StringType(), False),
            StructField("height", IntegerType(), True),
            StructField("weight", IntegerType(), True),
            StructField("base_experience", IntegerType(), True),
            StructField("type_1", StringType(), True),
            StructField("type_2", StringType(), True)
        ])

        # Création du DataFrame
        df = spark.createDataFrame(pokemon_data, schema)
        logger.info(f"DataFrame créé avec {df.count()} lignes")

        # Affichage des données pour vérification
        logger.info("Aperçu des données :")
        df.show(5)

        # Configuration de la connexion PostgreSQL
        postgres_properties = {
            "user": "airflow",
            "password": "airflow",
            "driver": "org.postgresql.Driver"
        }

        # Écriture dans PostgreSQL
        logger.info("Début de l'écriture dans PostgreSQL")
        df.write \
            .format("jdbc") \
            .option("url", "jdbc:postgresql://postgres:5432/airflow") \
            .option("dbtable", "pokemon_data") \
            .mode("overwrite") \
            .options(**postgres_properties) \
            .save()

        logger.info("Données écrites avec succès dans PostgreSQL")
        spark.stop()
        logger.info("Job terminé avec succès")

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du job: {str(e)}")
        if 'spark' in locals():
            spark.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()