"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-12 09:28:41 @PyCharm
Description: 
一般与 Flask-app 分开部署
				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
import time

from utils import db, cache

# 需要连接 Flask-app 的 redis
cache.start_redis_service()

def init_task_queue():
    """
    初始化任务队列
    :return:
    """
    # 1.获取数据库中的待执行订单
    data: list[dict] = db.fetch_all("select id from `order` where `status`=1", [])
    db_id_set = {item['id'] for item in data}

    # 2.获取 redis 中的待执行订单
    conn = cache.get_conn()
    total_count = conn.llen("task_queue")
    cache_id_list = conn.lrange("task_queue", 0, total_count)
    cache_id_set = set(cache_id_list)

    # 3.数据库中有的，而 redis 中没有的，向 redis 队列中添加
    id_needed_push = set(db_id_set - cache_id_set)
    if id_needed_push:
        conn.lpush("task_queue", *id_needed_push)

def update_order_status(status: int, order_id: int):
    db.update_one(
        "update `order` set `status`=%s where `id`=%s",
        [status, order_id]
    )


def process_task(order_id: int):
    """根据订单编号处理订单"""
    print(f"已拿到订单: {order_id}")
    # 1.在数据库中检查订单是否存在
    order = db.fetch_one("select * from `order` where `id`=%s", [order_id])
    if not order:
        return False, "订单不存在"
    # 2.更新订单状态：处理中
    update_order_status(2, order["id"])
    # 3.处理订单
    print("处理订单: ", order)
    time.sleep(5)

    # 4.更新订单状态：成功/失败
    update_order_status(3, order["id"])

    return True, "订单已处理"


def run():
    init_task_queue()

    while True:
        order_id = cache.pop_queue("task_queue", 10)
        if not order_id:
            continue
        process_task(order_id)


if __name__ == '__main__':
    run()