# coding=utf-8

import logging
import redis

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session
from config import Config,config
from utils.commons import RegexConverter
from logging.handlers import RotatingFileHandler


# 创建数据库对象--数据库配置config.py
db = SQLAlchemy()
# 创建redis对象，存储项目数据用--redis配置config.py
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 使用wtf提供的csrf保护机制--配置config.py密钥
csrf = CSRFProtect()

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式
formatter = logging.Formatter("%(levelname)s %(filename)s:%(lineno)d %(message)s") # 日志等级，输入日志信息的文件名，行数，日志信息
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（应用程序实例app使用的）添加日后记录器
logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """创建flask应用app对象"""
    app = Flask(__name__)
    # 从配置对象中为app设置配置信息--config.py
    app.config.from_object(config[config_name])

    # 为app中的url路由添加正则表达式匹配--utils/commons.py
    app.url_map.converters["regex"] = RegexConverter

    # 数据库处理
    db.init_app(app)
    # 为app添加CSRF保护
    csrf.init_app(app)

    # 使用flask-session扩展，用redis保存app的session数据--config.py
    Session(app)

    # 为app添加api蓝图应用--ihome/api_1_0/__init__.py
    from .api_1_0 import api as api_1_0_blueprint
    # 注册蓝图，配置调用接口url_prefix
    # 在manage.py中app的url_map将包含api,匹配路径后会自动添加url_prefix
    app.register_blueprint(api_1_0_blueprint, url_prefix="/api/v1.0")

    # 为app添加返回静态html的蓝图应用
    from web_page import html as html_blueprint
    # 注册蓝图
    app.register_blueprint(html_blueprint)

    return app
