# coding=utf-8

# 导入蓝图对象
from . import api
# 导入图片验证码拓展包
from ihome.utils.captcha.captcha import captcha
# 导入数据库实例
from ihome import redis_store,constants,db
# 导入flask内置对象
from flask import current_app,make_response,request,jsonify,session
# 导入自定义状态码
from ihome.utils.response_code import RET
# 导入模型类
from ihome.models import User
# 导入云通讯拓展包
from ihome.utils import sms
import re
import random

@api.route("/imagecode/<image_code_id>", methods=["GET"])
def generate_image_code(image_code_id):
    """
    生成图片验证码
    1/调用captcha扩展包,生成图片验证码,name,text,image
    2/本地存储图片验证码,使用redis数据库
    3/返回图片本身,设置响应
    :param image_code_id:
    :return:
    """
    # 调用captcha拓展包，生成图片验证码
    name,text,image = captcha.generate_captcha()
    # 调用redis数据库实例，存储图片验证码,设置过期时间ex
    try:
        redis_store.setex("ImageCode_"+image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 调用应用上下文，记录项目错误日志信息
        current_app.logger.error(e)
    # 未发生异常，返回图片image
    else:
        # 使用响应对象，用来返回图片
        response = make_response(image)
        # 设置响应报文的Content-Type
        response.header["Content-Type"] = "image/jpg"
        # 响应结果
        return response



@api.route("/smscode/<mobile>", methods=["GET"])
def send_sms_code(mobile):
    """
    发送短信:获取参数--校验参数--查询数据--返回结果
    1/获取参数,图片验证码和编号
    2/校验参数的完整性,mobile,text,id
    3/检查mobile手机号格式
    4/获取本地存储的真实图片验证码
    5/判断获取结果,图片验证码是否过期
    6/删除图片验证码
    7/比较图片验证码
    8/查询数据库,判断手机号是否已经注册
    9/生成短信内容,随机数
    10/保存短信内容到redis中
    11/调用云通讯发送短信
    12/保存返回结果,判断是否发送成功
    13/返回结果
    :param mobile:
    :return:
    """
    # 获取参数
    image_code = request.args.get("text")
    image_code_id = request.args.get("id")
    # 检查参数完整性
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")
    # 校验手机号格式
    if not re.match(r"1[3-9]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    # 检查图片验证码，从redis中获取正确的图片验证码
    try:
        real_image_code = redis_store.get("ImageCode_"+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询图片验证码失败")
    # 校验验证码是否过期
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码过期")
    # 删除图片验证码，图片验证码只使用一次
    try:
        redis_store.delete("ImageCode_"+image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 比较图片验证码是否一致，忽略大小写
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")

    # 查询数据库，获取user对象
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")
    else:
        # 判断手机号是否已存在
        if user:
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已注册")

    # 构造短信验证码，生成6位随机数
    sms_code = "%06d" % random.randint(0,999999)
    # 保存短信验证码到redis中
    try:
        redis_store.setex("SMSCode_"+mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")

    # 调用云通讯拓展包，发送短信
    try:
        cpp = sms.CCP()
        result = cpp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信异常")
    # 判断是否发送成功
    if 0 == result:
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")

# url采用/user符合restful风格
@api.route("/user", methods=["POST"])
def register():
    """

    :return:
    """
    # 获取参数,字典格式
    user_data = request.get_json()
    # 判断获取结果
    if not user_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 获取详细参数信息
    mobile = user_data.get("mobile")
    sms_code = user_data.get("sms_code")
    password = user_data.get("password")
    # 检查参数完整性
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")
    # 校验手机号格式
    if not re.match(r"1[3-9]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")
    # 判断用户是否已存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")
    else:
        # 判断手机号是否已存在
        if user:
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已注册")

    # 获取redis中正确的短信验证码
    try:
        real_sms_code = redis_store.get("SMSCode_"+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")
    # 判断验证码是否过期
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期")
    # 直接比较短信验证码是否正确
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")
    # 删除短信验证码
    try:
        redis_store.delete("SMSCode_"+mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 创建User实例，用于保存数据操作
    user = User(mobile=mobile, name=mobile)
    # 调用模型类中额的方法generate_password_hash,对密码进行加密sha256处理
    user.password = password
    # 提交数据到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 如果提交数据发生异常，需要进行回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户信息失败")
    # 缓存用户信息
    session["user_id"] = user.id
    session["mobile"] = mobile
    session["name"] = mobile
    # 返回结果
    # 返回data，前段若需要就可以直接使用了
    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())
