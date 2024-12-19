from vanna.flask import VannaFlaskApp
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

import psycopg2
import pandas as pd

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

vn = MyVanna(config={'model': 'llama3.2-vision'})


# 連接到 SQLite 資料庫
#vn.connect_to_postgres(host='10.10.10.168', dbname='postgres', user='admin', password='admin', port='5432')

def run_sql(sql: str) -> pd.DataFrame:
    with psycopg2.connect(
        host='10.10.10.168',
        database='postgres',
        user='admin',
        password='admin',
        port='5432'
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(result, columns=columns)
            return df

vn.run_sql = run_sql
vn.run_sql_is_set = True

# 建立查詢
def ask_question():
    response = vn.ask("請問AP的資料表有哪些欄位?")
    return response

if __name__ == "__main__":
    # 建立 Flask 應用程式
    app = VannaFlaskApp(vn, allow_llm_to_see_data=True)
    app.run(host='0.0.0.0', port=8080)
