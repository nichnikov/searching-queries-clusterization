import os
import psycopg2
import pandas as pd
from contextlib import suppress
from psycopg2 import Error
from sqlalchemy import create_engine 
from src.config import logger
from src.schemas import UserQuery
from src.clusterer import user_queries_clustering
from pydantic.error_wrappers import ValidationError


try:
    connection = psycopg2.connect(user=os.environ['USER'], 
                                password=os.environ['PASSWORD'], 
                                host=os.environ['HOST'], 
                                port="5432", 
                                database=os.environ['DB_NAME'])

    cursor = connection.cursor()

    cursor.execute('SELECT * FROM kharlashin.hs_test_data_for_reform_recognition_dev')
    rows = cursor.fetchall()
    logger.info("Из БД получено {} записей".format(len(rows)))

except (Exception, Error) as error:
    logger.error("Ошибка при работе с PostgreSQL", error)

finally:
    if connection:
        cursor.close()
        connection.close()
        logger.info("Соединение с PostgreSQL закрыто")

data = [UserQuery(*row) for row in rows]
data_df = pd.DataFrame(data)
logger.info("Данные из БД преобразованы в DataFrame размера {}".format(str(data_df.shape)))


result_df = user_queries_clustering(data_df)
conn_string = os.environ['SQLALCHEMY_CON']
db = create_engine(conn_string)
conn = db.connect() 

result_df.to_sql("queries_with_clusters", con=conn, if_exists='replace', index=False)

# 94463