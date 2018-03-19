# coding=utf-8
# 导入蓝图对象
from . import api,
# 导入flask封装的对象
from flask import request,jsonify,current_app,session,g
# 导入自定义状态码
from ihome.utils.response_code import RET
# 导入模型类
from ihome.models import User
# 导入登陆验证装饰器
from ihome.utils.commons import login_required
# 导入数据库实例
from ihome import db,constants
# 导入七牛云拓展包
from ihome.utils.image_storage import storage
# 导入正则
import re



@api.route("/sessions", methods=["POST"])
def login():
    """
     用户登陆
    1/获取参数,request.get_json()
    2/检查获取结果
    3/获取json数据包的详细参数信息,mobile/password
    4/检查参数的完整性
    5/检查手机号的格式
    6/查询数据库,确认用户已注册,保存查询结果
    7/密码检查:使用模型类对象调用密码检查方法check_password_hash(password)
    user.password = password --->generate_password_hash
    8/缓存用户信息:
    session['name'] = mobile
    session['name'] = user.name
    9/返回结果
    :return:
    """
    # 获取post请求参数
    user_data = request.get_json()
    # 校验参数
    if not user_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 获取详细参数信息mobile,password
    mobile = user_data.get("mobile")
    password = user_data.get("password")
    # 校验参数完整性
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 校验手机号格式
    if not re.match(r"1[3456789]{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")
    # 查询数据库
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")
    # 校验查询结果，确认用户和密码是否正确
    # 调用User的方法check_password判断密码是否相同
    if not user or not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")
    # 缓存用户信息
    session["user_id"] = user.id
    session["mobile"] = mobile
    # 用户可能修改了用户名信息
    session["name"] = user.name
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="OK", data={"user_id":user.id})

@api.route("/user", methods=["get"])
@login_required
def get_user_profile():
    """
     获取用户信息
    1/获取用户身份
    user_id = g.user_id
    2/根据用户身份查询数据库
    user = User.query.get(user_id)
    user = User.query.filter_by(id=user_id).first()
    3/校验查询结果
    4/返回结果,需要调用模型类中to_dict()方法
    :return:
    """
    # 获取用户id
    user_id = g.user_id
    # 查询数据库
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库错误")
    # 判断查询结果
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="查询数据库错误")
    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())
