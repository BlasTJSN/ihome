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

#### 2. 项目启动设置--配置config.py,manage.py,ihome/__init__.py
2.1 实现__init__.py中初始化逻辑
        创建数据库对象db
        创建redis对象redis_store
        使用wtf提供的csrf保护机制

        设置日志的记录等级
        创建日志记录器，指明日志保存的路径，每个日志文件的大小，保存日志文件个数上限
        创建日志记录格式
        为刚创建的日志记录器设置日志记录格式
        为全局的日志工具对象（应用程序实例app使用的）添加日后记录器

        定义创建app对象函数
            创建Flask对象app
            从配置对象中为app设置配置信息--config.py
            为app中的url路由添加正则表达式匹配--utils/commons.py

            数据库处理--SQLAlchemy(app)
            添加CSRF保护--CSRFProtect(app)
            使用flask_session扩展，用redis保存app保护的session数据--config.py

            为app添加api蓝图应用--ihome/api_1_0/__init__.py

            为app添加返回静态html的蓝图应用--ihome/web_page.py

            返回app对象

2.2 配置config.py
        定义Config类
            设置SECRET_KEY
            设置sqlalchemy数据库使用参数
            设置reids参数
            设置session参数
        定义开发模式子类，继承Config
            设置DEBUG=True
        定义生产环境子类，继承Config
            设置DEBUG=False
        构造config字典

2.3 在ihome/utils/response_code.py中添加自定义状态码

2.4 实现ihome/utils/commons.py中的正则表达转换器和用户登陆验证装饰器逻辑
        定义正则转换器类，继承BaseConverter
            实现逻辑
        定义用户登陆验证装饰器
            获取session中的user_id
            判断是否存在
                不存在，未登录，返回json
                存在，将user_id存储在临时变量g中，返回调用的函数

2.5 实现ihome/api_1_0/__init__.py中创建蓝图和设置钩子--设置默认响应报文格式的逻辑
        定义蓝图对象api
        设计@api.after_request请求钩子
            判断响应报文response的Content-Type是否以text开头
                是，改成默认的json类型"application/json"
            返回response

2.6 实现ihome/web_page.py中创建蓝图和正则静态路由页面访问逻辑
        定义蓝图对象html
        设计@html.route("/<regex(.*):file_name>")装饰器路由
            判断file_name是否存在
                不存在，赋值为"index.html"
            判断file_name是否等于favicon.com
                不等于，将file_name修改为"html/"+file_name
            生成csrf_token
            定义响应报文response
            设置csrf_token的cookie
            响应结果，返回response

2.7 实现manage.py项目启动逻辑
        创建项目应用对象app
        数据库迁移
        添加终端运行命令
        添加终端导出数据库迁移命令
        运行app
2.8 ihome/constants.py中添加通用数据
2.9 实现ihome/utils/sms.py中的逻辑
    2.8.1 注册'容联云通讯' www.yuntongxun.com，在utils文件夹下的sms.py文件里修改配置
    2.8.2 定义发送短信辅助类


2.10 实现ihome/utils/image_storage.py中的逻辑
    2.10.1 注册'七牛云' www.qiniu.com，在utils文件夹下的image_storage.py文件里修改配置信息，在constants.py文件里修改七牛的空间外链域名
    2.10.2 定义七牛云存储上传文件接口类


2.11