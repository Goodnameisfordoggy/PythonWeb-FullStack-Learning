"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-23 22:27:06 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""

class Paginator:
    """分页工具"""
    def __init__(self, queryset, page: int, page_size: int):
        # 原始数据集
        self.queryset = queryset
        # 当前页码
        self.page = self._validate_page(page)
        # 每页数据条数
        self.page_size = page_size
        # 总数据条数
        self.total_count = len(queryset)
        # 分页切片的起点，终点
        self.start = (self.page - 1) * self.page_size
        self.end = min(self.page * self.page_size, self.total_count)

    def _validate_page(self, page):
        """校验页码合法性"""
        try:
            page = int(page)
            return page if page >= 1 else 1 # 页码至少为1
        except (TypeError, ValueError):
            return 1  # 非法页码默认返回第1页

    @property
    def total_pages(self):
        """计算总页数"""
        if self.total_count == 0:
            return 1
        return (self.total_count + self.page_size - 1) // self.page_size  # 向上取整

    @property
    def paginated_data(self):
        """获取当前页的数据切片"""
        return self.queryset[self.start:self.end]
