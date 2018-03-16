# ihome
爱家房租项目

#### 1. 项目准备
1.1 创建虚拟环境Flask_ihome，安装requirements.txt中的依赖包
1.2 建立ihome项目文件
    1.2.1 建立api_1_0目录存放项目视图函数--后端接口
    1.2.2 建立libs目录存放项目甬道的第三方拓展
        1.2.2.1 建立yuntongxun目录，第三方拓展--发送短信
    1.2.3 建立static目录存放项目静态文件
        1.2.3.1 建立css目录，存放项目css文件
        1.2.3.2 建立html目录，存放项目html文件
        1.2.3.3 建立images目录，存放项目images文件
        1.2.3.4 建立js目录，存放项目js文件
        1.2.3.5 建立plugins目录，存放项目前端插件--bootstrap,switch,swiper等
        1.2.3.6 favicon.ico,项目logo
    1.2.4 建立utils目录存放项目通用工具
        1.2.4.1 建立captcha目录，图片验证码生成
        1.2.4.2 新建commons.py作为通用设施文件--正则url,登陆验证装饰器
        1.2.4.3 新建image_storage.py作为云存储设施文件--七牛云
        1.2.4.4 新建response_code.py，自定义状态码
        1.2.4.5 新建sms.python，发送短信
    1.2.5 新建__init__.py作为项目应用初始化文件--应用程序实例，数据库实例，蓝图，日志等
    1.2.6 新建constants.py存放项目常量信息--数据库缓存信息，验证码，房屋信息等
    1.2.7 新建models.py定义项目模型类
    1.2.8 新建web_page.py视图函数--用来处理静态页面的访问

1.3 新建manage.py作为项目启动文件
1.4 新建config.py作为项目配置文件
1.5 建立ihome目录作为项目应用核心目录
1.6 建立logs目录存放项目日志
1.7