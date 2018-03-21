# coding=utf-8

from flask import Blueprint

api = Blueprint("api", __name__)

# 把拆分出去的蓝图导入到创建蓝图的地方
import register,passport,house


@api.after_request
def after_request(response):
    """设置默认的响应报文格式为application/json"""

    # 如果响应报文response的Content-Type是以text开头，则将其改为默认的json类型
    if response.header.get("Content-Type").startswith("text"):
        response.header["Content-Type"] = "application/json"
    return response