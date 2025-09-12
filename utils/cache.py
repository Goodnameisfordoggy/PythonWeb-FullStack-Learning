"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-11 13:35:24 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
import os
import redis
import platform
import subprocess
from redis import ConnectionPool

REDIS_INSTALL_PATH = r"F:\Redis-x64-3.2.100"
REDIS_SERVER_EXE = os.path.join(REDIS_INSTALL_PATH, "redis-server")
# 配置 Redis POOL 连接信息
REDIS_CONNPOOL_PARAMS = {
    'host': '127.0.0.1',  # Redis服务器地址
    'port': 6379,  # Redis端口
    'db': 0,  # 使用的数据库编号
    'password': None,  # 密码，如果有的话
    'decode_responses': True,  # 自动将字节转换为字符串
    'max_connections': 10  # 连接池最大连接数
}


# 一般一个项目仅需一个连接池，单例模式的连接池：
class RedisPool:
    _instance = None

    @classmethod
    def get_instance(cls):
        """获取连接池实例"""
        if cls._instance is None:
            cls._instance = ConnectionPool(**REDIS_CONNPOOL_PARAMS)
        return cls._instance

def get_conn():
    conn = redis.Redis(connection_pool=RedisPool.get_instance())
    return conn

def check_redis_service_status() -> (bool, str):
    """通过 Windows 的 sc 命令检查 Redis 服务状态（兼容旧版本）"""
    try:
        # 查询Redis服务状态（默认服务名为"Redis"）
        result = subprocess.run(
            ["sc", "query", "Redis"],
            capture_output=True,
            text=True,
            check=True
        )
        # print(result.stdout)
        # 服务运行中会包含"RUNNING"关键字
        if "RUNNING" in result.stdout:
            return True, "Redis服务正在运行..."
        else:
            return False, f"Redis服务未运行，状态信息：{result.stdout}"
    except subprocess.CalledProcessError:
        # 服务未安装时会报错，返回未安装状态
        return False, "Redis服务未安装（未找到服务）"
    except Exception as e:
        return False, f"查询失败：{str(e)}"


def start_redis_service():
    """根据操作系统启动 Redis 服务"""
    os_type = platform.system()
    try:
        if os_type == "Linux":
            # # Linux系统使用systemctl启动
            # subprocess.run(
            #     ["sudo", "systemctl", "start", "redis-server"],
            #     check=True,
            #     capture_output=True,
            #     text=True
            # )
            pass
        elif os_type == "Windows":
            # 检测服务是否启动
            status, message = check_redis_service_status()
            if status:
                print(message)
                return True
            # Windows系统启动 Redis 服务
            subprocess.run(
                [REDIS_SERVER_EXE, "--service-start"],
                check=True,
                capture_output=True,
                text=True
            )
        elif os_type == "Darwin":  # macOS
            # # macOS使用brew启动
            # subprocess.run(
            #     ["brew", "services", "start", "redis"],
            #     check=True,
            #     capture_output=True,
            #     text=True
            # )
            pass
        else:
            print(f"不支持的操作系统: {os_type}")
            return False

        print("Redis服务已成功启动")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Redis服务启动失败: {e.stderr}")
        return False


def push_queue(value, key):
    """入队"""
    conn = redis.Redis(connection_pool=RedisPool.get_instance())
    conn.lpush(key, value)


def pop_queue(key, timeout=10):
    """出队"""
    conn = redis.Redis(connection_pool=RedisPool.get_instance())
    data = conn.brpop(key, timeout=timeout)
    # print(data)
    if not data:
        return None
    # return data[1].decode('utf-8')
    return data[1]


def list_iter(name):
    """
    redis 列表增量迭代器
    :param name: redis 列表的名称
    :return: yield 单个列表元素
    """
    conn = redis.Redis(connection_pool=RedisPool.get_instance())
    total_count = conn.llen(name)
    for index in range(total_count):
        yield conn.lindex(name, index)


# if __name__ == "__main__":
#     start_redis_service()