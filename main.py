"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-07 22:10:32 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from flask_app import create_app
from utils.cache import start_redis_service

app = create_app()

if __name__ == '__main__':
    start_redis_service()
    app.run(debug=True)