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

(venna) root@user-8700:~/nick_test/venna# cat train.py
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore


class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

#vn = MyVanna(config={'model': 'mistral'})
vn = MyVanna(config={'model': 'llama3.2-vision'})
vn.connect_to_postgres(host='10.10.10.168', dbname='postgres', user='admin', password='admin', port='5432')

 # The information schema query may need some tweaking depending on your database. This is a good starting point.
df_information_schema = vn.run_sql("SELECT * FROM public.ap ;")

vn.train(ddl="""
CREATE TABLE public.ap (
        公司 varchar(8) NULL,
        部門別 varchar(8) NULL,
        應付帳款類型 varchar(4) NULL,
        採購單號 int4 NULL,
        供應商 varchar(32) NULL,
        供應商編號 int4 NULL,
        發票日期 date NULL,
        總帳日期 date NULL,
        總帳月份 date NULL,
        "發票金額(未稅)" varchar(16) NULL,
        稅金額 varchar(16) NULL,
        發票總金額 varchar(16) NULL,
        發票號碼 varchar(32) NULL,
        立帳幣別 varchar(4) NULL,
        付款幣別 varchar(4) NULL,
        付款條件 varchar(32) NULL,
        預計付款日期 date NULL,
        付款方式 varchar(2) NULL,
        付款基準日 date NULL,
        對應類型 varchar(16) NULL,
        匯率日期 date NULL,
        匯率 int4 NULL,
        供應商銀行 varchar(64) NULL,
        供應商帳號 varchar(16) NULL,
        摘要說明 varchar(128) NULL
);
""")

#vn.train(sql="SELECT * FROM public.ar WHERE 部門別 = 'ABC 作業單位'")

# This will break up the information schema into bite-sized chunks that can be referenced by the LLM
#plan = vn.get_training_plan_generic(df_information_schema)

#print(plan)

#vn.train(plan=plan)

#training_data = vn.get_training_data()
#print(training_data)

#vn.ask(question="請問總金額有多少?")
#vn.remove_training_data(id='6d2f5ad4-df5c-51ed-8304-959699cc7e5f-sql')