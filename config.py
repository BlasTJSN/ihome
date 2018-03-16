# coding=utf-8

import redis

class Config:
    """基本参数配置"""
    SECRET_KEY = "cHl0aG9uZmxhc2tpaG9tQmxhc3RKU04="
    # flask-sqlalchemy使用的参数
    # mysql数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost/ihome"
    # 动态追踪数据库修改行为
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 创建redis实例用到的参数
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask-session使用的参数，用于保存session到redis
    SESSION_TYPE = "redis" # 指定保存session数据的地方
    SESSION_USE_SIGNER = True # 为session id进行签名
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT) # 配置保存session的redis
    PERMANENT_SESSION_LIFETIME = 86400 # session数据有效时间


class DevelopmentConfig(Config):
    """开发者模式的配置参数"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境模式的配置参数"""
    pass # 默认debug=False

# 定义字典
config = {
    "development":DevelopmentConfig,
    "production":ProductionConfig
}