import os
import pandas as pd
from sqlalchemy import create_engine 
from src.config import logger
from src.clusterer import user_queries_clustering


conn_string = os.environ['SQLALCHEMY_CON']
db = create_engine(conn_string)
conn = db.connect() 

data_df = pd.read_sql_table("hs_test_data_for_reform_recognition_dev", schema="kharlashin", con=conn)
data_df.rename(columns={"new_licensesId": "new_licensesId",
                        "new_BitrixId": "BitrixId",
                        "servertimestamp": "serverTimestamp",
                        "payload__request_string": "payload_request_string"}, 
               inplace=True)

result_df = user_queries_clustering(data_df)
result_df.to_sql("queries_with_clusters", con=conn, if_exists='replace', index=False)
conn.close()