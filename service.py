import os
import psycopg2
import pandas as pd
from contextlib import suppress
from psycopg2 import Error
from pydantic.error_wrappers import ValidationError
from src.config import logger
from src.schemas import UserQuery
from src.clusterer import user_queries_clustering


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

data = []
for row in rows:
    with suppress(ValidationError):
        data.append(UserQuery(*row))

data_df = pd.DataFrame(data)
logger.info("Данные из БД преобразованы в DataFrame размера {}".format(str(data_df.shape)))

result_df = user_queries_clustering(data_df)
result_df.to_csv("queries_with_clusters.csv", sep="\t", index=False)

'''
# with mistakes analysis:
mistakes = []
for row in rows:
    try:
        data.append(UserQuery(LicensesId=row[0], BitrixId=row[1], Date=row[2], Query=row[3]))
    except ValidationError:
        mistakes.append(row) 

print(mistakes)
'''
