import sqlite3
import pandas as pd
import os

print(os.getcwd())
dbname = 'nisa.db'
df = pd.read_csv("/workspaces/python_env/finance_data.csv")
conn = sqlite3.connect(dbname)
# cur = conn.cursor()

# df.to_sql('sample', conn, if_exists='replace')

# # 作成したデータベースを1行ずつ見る
# select_sql = 'SELECT * FROM sample limit 10'
# for row in cur.execute(select_sql):
#     print(row)

# cur.close()
conn.close()
