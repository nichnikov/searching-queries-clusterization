import os
import pandas as pd
from itertools import groupby
from operator import itemgetter
from src.start import tokenizer, vectorizer
from src.config import logger
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer


def grouped_func(data: list) -> list[dict]:
    """Function groups input list of data with format: [(label, vector, text)]
    into list of dictionaries, each dictionary of type:
    {
    label: label,
    texts: list of texts correspond to label
    vectors_matrix: numpy matrix of vectors correspond to label
    }
    """
    data = sorted(data, key=lambda x: x[0])
    grouped_data = []
    for key, group_items in groupby(data, key=itemgetter(0)):
        d = {"label": key, "texts": []}
        for item in group_items:
            d["texts"].append(item[1])
        grouped_data.append(d)
    return grouped_data


def clustering_func(vectorizer: SentenceTransformer, clusterer: AgglomerativeClustering, texts: list) -> list[dict]:
    """Function for text collection clustering"""
    vectors = vectorizer.encode([str(x).lower() for x in texts])
    clusters = clusterer.fit(vectors)
    data = [(lb, tx) for lb, v, tx in zip(clusters.labels_, vectors, texts)]
    grouped_data = grouped_func(data)
    result_list = []
    for d in grouped_data:
        label = str(d["label"])
        cluster_size = len(d["texts"])
        result_list += [{"cluster_num": label, "lem_request_string": tx, "cluster_size": cluster_size} for tx in d["texts"]]
    return result_list

clusterer = AgglomerativeClustering(n_clusters=None, distance_threshold=1.0, memory=os.path.join("cache"))

def user_queries_clustering(df: pd.DataFrame):
    df["serverTimestamp"] = df["serverTimestamp"].astype("datetime64[ns]")        
    texts = [str(tx) for tx in df["payload_request_string"].to_list()]
    
    # добавим лемматизированные тексты:
    df = pd.DataFrame([{**d, **{"lem_request_string": " ".join(lm_tx)}} for lm_tx, d in 
                            zip(tokenizer(texts), df.to_dict(orient="records"))])

    result_dfs = []

    for date in df["serverTimestamp"].unique():
        one_day_df = df[df["serverTimestamp"] == date]
        tms_grp_df = one_day_df[["new_licensesId", "serverTimestamp"]].groupby("new_licensesId", as_index=False).count()
        users_more_one_query = tms_grp_df["new_licensesId"][tms_grp_df["serverTimestamp"] > 1].to_list()
        
        users_more_one_query_dfs = [one_day_df[:][one_day_df.new_licensesId == user_id] for user_id in users_more_one_query]

        for user_queries_df in users_more_one_query_dfs:
            clustering_dicts_df = pd.DataFrame(clustering_func(vectorizer, clusterer, user_queries_df["lem_request_string"].to_list()))
            temp_clustering_user_df = pd.merge(user_queries_df, clustering_dicts_df, on="lem_request_string")
            temp_clustering_user_df.drop_duplicates(inplace=True)
            result_dfs.append(temp_clustering_user_df)
        
        user_with_one_query_df = one_day_df[~one_day_df["new_licensesId"].isin(users_more_one_query)].assign(cluster_num=0, cluster_size=1)
        result_dfs.append(user_with_one_query_df)
    
    result_df = pd.concat(result_dfs, axis=0)
    
    result_df["new_licensesId"] = result_df["new_licensesId"].astype("string")
    result_df["payload_request_string"] = result_df["payload_request_string"].astype("string")
    result_df["cluster_num"] = result_df["cluster_num"].astype(int)

    logger.info("Результирующий датафрейм с размерностью: {}".format(str(result_df.shape)))
    result_df.drop("lem_request_string", axis=1, inplace=True)

    return result_df
        
        