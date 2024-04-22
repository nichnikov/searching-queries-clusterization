
import os
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

connection = psycopg2.connect(user=os.environ['USER'], 
                              password=os.environ['PASSWORD'], 
                              host=os.environ['HOST'], 
                              port="5432", 
                              database=os.environ['DB_NAME'])

cursor = connection.cursor()

cursor.execute('SELECT * FROM kharlashin.hs_test_data_for_reform_recognition_dev')
rows = cursor.fetchall()
cursor.close() # закрываем курсор

print(rows[:10])
print(len(rows))
