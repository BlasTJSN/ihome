# coding=utf-8
# 导入蓝图对象
from . import api
# 导入redis实例
from ihome import redis_store, constants,db
# 导入flask内置对象
from flask import current_app, jsonify, g, request
# 导入模型类
from ihome.models import Area, House, Facility, HouseImage
# 导入自定义状态码
from ihome.utils.response_code import RET
# 导入登陆验证装饰器
from ihome.utils.commons import login_required
# 导入七牛云
from ihome.utils.image_storage import storage

# 导入json模块
import json


@api.route("/areas", methods=["GET"])
def get_areas_info():
    """
    获取城区信息:
    缓存----磁盘----缓存
    1/尝试从redis中获取城区信息
    2/判断查询结果是否有数据,如果有数据
    3/留下访问redis的中城区信息的记录,在日志中
    4/需要查询mysql数据库
    5/判断查询结果
    6/定义容器,存储查询结果
    7/遍历查询结果,添加到列表中
    8/对查询结果进行序列化,转成json
    9/存入redis缓存中
    10/返回结果
    :return:
    """
    # 尝试从redis中获取程序信息
    try:
        areas = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
        # 发生异常，把查询结果设置为None
        areas = None
    # 判断查询结果是否存在
    if areas:
        return '{"errno":0,"errmsg":"OK","data":%s}' % areas

    # 查询数据库
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询城区信息异常")
    # 判断查询结果
    if not areas:
        return jsonify(errno=RET.NODATA, errmsg="无城区信息")
    # 定义容器
    areas_list = []
    for area in areas:
        # 需要调用模型类中的to_dict方法,把具体的查询对象转成键值形式的数据
        areas_list.append(area.to_dict())
    # 把城区信息转成json
    area_info = json.dumps((areas_list))
    # 存入redis
    try:
        redis_store.setex("area_info", constants.AREA_INFO_REDIS_EXPIRES, area_info)
    except Exception as e:
        current_app.logger.error(e)
    # 返回结果，城区信息已经是json字符串，不需要jsonify
    resp = '{"errno":0, "errmsg":"OK", "data":%s}' % area_info
    return resp