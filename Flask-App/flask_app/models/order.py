"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-14 00:43:23 @PyCharm
Description: 

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from datetime import datetime
from flask_app.models import db


class Order(db.Model):
    """订单模型"""
    __tablename__ = "order"
    __table_args__ = {
        'mysql_charset': 'utf8mb3',
        'mysql_collate': 'utf8mb3_general_ci'
    }

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 订单唯一标识
    order_identity = db.Column(db.String(64), nullable=False)

    # 创建时间：默认当前时间戳
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # 订单关联的URL
    url = db.Column(db.String(255), nullable=False)

    # 数量/次数
    count = db.Column(db.Integer, nullable=False)

    # 关联用户唯一标识
    user_identity = db.Column(db.String(64), nullable=False, comment='关联用户编号')

    # 订单状态：1=待处理，2=正在处理，3=成功，4=失败
    status = db.Column(db.SmallInteger, nullable=False, comment='状态：1=待处理，2=正在处理，3=成功，4=失败')

    # 逻辑删除标记：0=未删除，1=已删除
    is_deleted = db.Column(db.SmallInteger, nullable=False, default=0, comment='逻辑删除：0=未删除，1=已删除')

    # 代码层面的保护字段
    PROTECTED_FIELDS = {"id", "order_identity", "create_time", "user_identity"}

    def __repr__(self):
        return f'<Order (identity: {self.order_identity}, status: {self.status})>'

    @classmethod
    def create(cls, **kwargs):
        """
        创建一条新记录
        :param kwargs: 包含订单信息的关键字参数
        :return: (bool, str): (是否成功，反馈信息)
        """
        try:
            order = cls(**kwargs)
            db.session.add(order)
            db.session.commit()
            return order, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @classmethod
    def delete(cls, order_identity):
        """逻辑删除"""
        try:
            # 删除操作
            affected_rows = cls.query.filter_by(order_identity=order_identity, is_deleted=0).update({"is_deleted": 1})
            db.session.commit()
            # 根据受影响行数判断是否删除成功
            if affected_rows > 0:
                return True, "删除成功"
            else:
                return False, "订单不存在或已删除"
        except Exception as e:
            db.session.rollback()  # 出错时回滚
            return False, f"删除失败：{str(e)}"

    @classmethod
    def update_by_identity(cls, identity, **kwargs):
        """
        根据唯一标识更新
        :param identity: 唯一标识
        :param kwargs: 要更新的字段的关键字参数
        :return: (bool, str): (是否成功，反馈信息)
        """
        try:
            update_data = {k: v for k, v in kwargs.items() if k not in cls.PROTECTED_FIELDS}
            if not update_data:
                return False, "没有有效的更新字段"
            # 更新操作
            affected_rows = cls.query.filter_by(order_identity=identity).update(update_data)
            db.session.commit()
            # 根据受影响行数判断是否更新成功
            if affected_rows > 0:
                return True, "更新成功"
            else:
                return False, "订单不存在"
        except Exception as e:
            db.session.rollback()
            return False, f"更新失败：{str(e)}"

    @classmethod
    def get_by_order_identity(cls, order_identity):
        """通过订单唯一标识查询订单"""
        return cls.query.filter_by(order_identity=order_identity).first()

    @classmethod
    def get_by_user_identity(cls, user_identity):
        """查询指定用户的所有有效订单"""
        return cls.query.filter_by(user_identity=user_identity).all()

    # 需要特殊处理（如前置校验）的，单独封装
    @classmethod
    def update_status_by_identity(cls, order_identity, new_status):
        """通过订单标识直接更新状态"""
        # 验证状态值合法性
        if new_status not in [1, 2, 3, 4]:
            return False, f"无效的状态值{new_status},只能为1,2,3,4"

        try:
            # 执行更新操作
            result = cls.query.filter_by(order_identity=order_identity).update({
                'status': new_status
            })
            db.session.commit()
            # 是否有记录被更新，result为受影响的行数
            if result == 0:
                return False, "未找到对应的订单"
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)