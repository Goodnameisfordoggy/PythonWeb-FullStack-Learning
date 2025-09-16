"""
Author: HDJ @https://github.com/Goodnameisfordoggy
Time@IDE: 2025-09-13 23:53:40 @PyCharm
Description:

				|   早岁已知世事艰，仍许飞鸿荡云间；
				|   曾恋嘉肴香绕案，敲键弛张荡波澜。
				|
				|   功败未成身无畏，坚持未果心不悔；
				|   皮囊终作一抔土，独留屎山贯寰宇。

Copyright (c) 2024-2025 by HDJ, All Rights Reserved.
"""
from datetime import datetime
from . import db


class User(db.Model):
    """用户模型"""
    __tablename__ = "userinfo"
    __table_args__ = {
        'mysql_charset': 'utf8mb3',
        'mysql_collate': 'utf8mb3_general_ci'
    }

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 用户唯一标识
    user_identity = db.Column(db.String(64), nullable=False)

    # 创建时间：默认当前时间戳
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # 手机号
    mobile = db.Column(db.String(11), nullable=False)

    # 密码
    password = db.Column(db.String(128), nullable=False)

    # 姓名
    name = db.Column(db.String(32), nullable=False)

    # 角色
    role = db.Column(db.SmallInteger, nullable=False, comment='1=管理员，2=客户')

    # 逻辑删除标记：
    is_deleted = db.Column(db.SmallInteger, nullable=False, default=0, comment='0=未删除，1=已删除')

    def __repr__(self):
        return f'<User (name: {self.name}, id: {self.id})>'

    @classmethod
    def create(cls, **kwargs):
        """
        用户创建
        :param kwargs: 包含用户信息的关键字参数
        :return: 元组 (用户实例, 错误信息)
        """
        try:
            # 创建用户实例（** kwargs自动匹配字段）
            user = cls(**kwargs)
            # 添加到会话并提交
            db.session.add(user)
            db.session.commit()
            return user, None  # 成功：返回用户实例和None
        except Exception as e:
            db.session.rollback()
            return None, str(e)  # 失败：返回None和错误信息

    @classmethod
    def delete(cls, user_identity):
        """逻辑删除"""
        try:
            affected_rows = cls.query.filter_by(
                user_identity=user_identity, is_deleted=0
            ).update({"is_deleted": 1})
            db.session.commit()
            # 根据受影响行数判断是否删除成功
            if affected_rows > 0:
                return True, "删除成功"
            else:
                return False, "用户不存在或已删除"
        except Exception as e:
            db.session.rollback()
            return False, f"删除失败：{str(e)}"

    @classmethod
    def get_by_user_identity(cls, user_identity):
        """通过唯一标识查询用户"""
        return cls.query.filter_by(user_identity=user_identity, is_deleted=0).first()

    @classmethod
    def get_by_mobile(cls, mobile):
        """通过手机号查询用户"""
        return cls.query.filter_by(mobile=mobile, is_deleted=0).first()
