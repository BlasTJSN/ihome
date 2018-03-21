# coding=utf-8
# 导入蓝图对象
from . import api
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

@api.route("/user/name", methods=["PUT"])
@login_required
def change_user_profile():
    """
      修改用户信息
    1/获取用户身份
    2/获取参数,put请求里的json数据,request.get_json()
    3/判断获取结果是否有数据
    4/获取详细的参数信息,name
    5/查询数据库,执行update更新用户信息
    User.query.filter_by(id=user_id).update({'name':name})
    db.session.commit()
    6/更新缓存中的用户信息
    session['name'] = name
    7/返回结果
    :return:
    """
    # 获取用户id
    user_id = g.user_id
    # 获取参数
    user_data = request.get_json()
    # 判断参数是否存在
    if not user_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 获取详细参数name
    name = user_data.get("name")
    # 检验参数是否存在
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")
    # 更新用户的姓名信息
    try:
        User.query.filter_by(id=user_id).update({"name":name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 写入数据发生异常需要回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户信息异常")
    # 更新缓存中的用户信息
    session["name"] = name
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="OK", data={"name":name})

@api.route("user/avatar", methods=["POST"])
@login_required
def set_user_avatar():
    """
    设置用户头像
    1/确认用户身份
    2/获取参数,前端传过来的图片文件,request.files.get('avatar')
    3/读取图片文件对象的数据
    4/调用七牛云接口,上传用户头像
    5/保存上传的结果,七牛云会对图片文件名进行编码处理
    6/根据用户身份,保存用户头像的文件名
    7/拼接图片的绝对路径
    8/返回结果
    :return:
    """
    # 获取用户id
    user_id = g.iser_id
    # 获取图片文件
    avatar = request.files.get("avatar")
    # 读取图片文件，转换成七牛云能接受的bytes类型
    avatar_data = avatar.read()
    # 调用七牛云，实现图片上传
    try:
        image_name = storage(avatar_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片失败")
    # 把图片文件名保存到数据库中
    # db.session.add(user)数据库会话对象
    # 如果使用update则不需要添加数据库会话对象
    try:
        User.query.filter_by(id=user_id).update({"avatar_url":image_name})
        # 提交会话
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 写入数据失败，回滚会话
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户头像失败")
    # 拼接图片绝对路径
    image_url = constants.QINIU_DOMIN_PREFIX + image_name
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="OK", data={"avatar_url":image_url})


@api.route("user/auth", methods=["POST"])
@login_required
def set_user_auth():
    """
    设置用户实名信息:
    1/获取用户id
    2/获取参数post
    3/检查参数的存在
    4/获取详细的实名信息,real_name/id_card
    5/把用户实名信息写入到数据库中,确保实名认证只能执行一次
    User.query.filter_by(id=user_id,real_name=None,id_card=None).update({'......'})
    6/返回结果
    :return:
    """
    # 获取用户id
    user_id = g.user_id
    # 获取参数
    user_data = request.get_json()
    # 判断是否存在
    if not user_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 获取详细的参数信息
    real_name = user_data.get("real_name")
    id_card = user_data.get("id_card")
    # 检验参数完整性
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")
    # 保存用户实名信息到数据库，只执行第一次
    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None).update({"real_name":real_name, "id_card":id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户实名信息失败")
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="OK")

@api.route("/user/auth", methods=["GET"])
@login_required
def get_user_auth():
    """
    获取用户的实名信息
    1/获取用户身份id
    2/查询mysql数据库,确认用户的存在
    3/检查结果
    4/返回结果,用户的实名信息
    :return:
    """
    # 获取用户id
    user_id = g.user_id
    # 查询数据库
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户实名信息失败")
    # 判断查询结果
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="OK", data=user.auth_to_dict())
