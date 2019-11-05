from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import pymysql

try:

    con = pymysql.connect('localhost', 'root', '', 'amazon')
    cur = con.cursor()
    
    df = pd.read_csv('10222019.csv')
    skus = df['sku.1']
    
    for sku in skus:
        sql = "INSERT INTO csv(sku) VALUES (%s)"
        cur.execute(sql, (sku))
        con.commit()
    cur.close()
    print("Done")

except Exception as e:
    print(e)