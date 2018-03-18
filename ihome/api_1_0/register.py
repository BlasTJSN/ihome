# coding=utf-8

# 导入蓝图对象
from . import api
# 导入图片验证码拓展包
from ihome.utils.captcha.captcha import captcha
# 导入数据库实例
from ihome import redis_store,constants,db
# 导入flask内置对象
from flask import current_app,make_response

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

@api.route("/smscode/<mobile>", method=["GET"])
def send_sms_code(mobile):
    pass







