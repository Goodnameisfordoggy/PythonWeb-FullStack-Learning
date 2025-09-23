"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-22 23:45:23 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
import hashlib
import uuid
import time


def generate_sha256_identifier(input_data: str | None = None):
    """
    生成基于 SHA256 的唯一标识

    参数:
        input_data: 可选，自定义输入数据（如用户信息、时间戳等）
                    若为 None，则自动生成随机数据

    返回:
        str: 64 位的 SHA256 哈希字符串
    """
    if input_data is None:
        # 如果没有提供输入，使用随机 UUID + 时间戳作为原始数据减少碰撞概率
        raw_data = f"{time.time()}-{uuid.uuid4()}"
    else:
        # 确保输入是字符串类型，接上时间戳减少碰撞概率
        raw_data = str(input_data) + f"{time.time()}"
    # 转换为字节流（SHA256 要求输入为 bytes 类型）
    byte_data = raw_data.encode('utf-8')
    # 计算 SHA256 哈希
    sha256_hash = hashlib.sha256(byte_data).hexdigest()
    return sha256_hash

