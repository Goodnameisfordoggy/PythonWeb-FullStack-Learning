"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-08 00:08:33 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
import pymysql
from pymysql import cursors
from dbutils.pooled_db import PooledDB

MYSQL_CONN_POOL = PooledDB(
    creator=pymysql,
    maxconnections=10,
    mincached=2,
    maxcached=5,  # 最大空闲链接数
    blocking=True,  # 全部占用时是否阻塞等待
    setsession=[],
    ping=0, # 链接可用检测
    host="127.0.0.1", port=3306, user="root", passwd="root", charset="utf8", db="flask-app"
)

def fetch_one(sql, param) -> dict | None:
    conn = MYSQL_CONN_POOL.connection()
    cursor = conn.cursor(cursors.DictCursor)
    cursor.execute(sql, param)
    result = cursor.fetchone()
    cursor.close()
    conn.close()    # 将连接反还回给连接池
    return result

def fetch_all(sql, param) -> list[dict] | None:
    conn = MYSQL_CONN_POOL.connection()
    cursor = conn.cursor(cursors.DictCursor)
    cursor.execute(sql, param)
    result = cursor.fetchall()
    cursor.close()
    conn.close()    # 将连接反还回给连接池
    return result