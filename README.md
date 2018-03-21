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


2.11 ihome/libs/yuntongxun

2.12 ihome/utils/captcha

#### 3. ihome/models.py定义模型类
3.1 python manage.py db init 创建migrations文件夹，存放迁移文件
3.2 python manage.py db migrate -m 'initial migration' 迁移模型类
3.3 python manage.py db upgrade

#### 4. 用户注册 新增--ihome/static/js/ihome/register.js
4.1 新建register.py文件，在ihome/api_1_0/__init__.py中导入register模块
4.2 实现生成图片验证码逻辑
        调用captcha拓展包，生成图片验证码返回name,text,image
        获取前端生成的image_code_id(UUID)
        调用redis对象存储图片验证码text到redis中，key采用name_+UUID形式
        调用make_response,返回image
        设置响应的Content-Type
        响应结果，返回response
4.3 实现发送短信逻辑
        获取参数mobile,text,id
        校验参数
            判断参数完整性
            判断手机号格式
        获取redis存储的验证码text
        判断验证码是否过期
            过期，删除验证码
        比较验证码
        判断手机号是否已注册
        生成短信内容，生成6位随机数
        保存随机数到redis中
        调用云通讯发送短信，保存响应结果
        根据响应结果判断是否发送成功
        返回结果

4.4 实现注册逻辑
        获取参数request.get_json()
        检验参数
        获取详细参数
        校验手机号格式
        判断用户是否已存在
        校验短信验证码
        获取redis存储的短信验证码
        判断验证码是否过期
        比较短信验证码是否正确
        删除短信验证码
        保存用户数据
        缓存用户数据
        返回结果

前段：三元表达式 条件满足执行？后第一个，不满足执行？后面第二个

def send_sms_code
sample(list, k) 从列表中随机获取k个元素


#### 5. 实现passport.py中的逻辑，在ihome/api_1_0/__init__.py中导入register模块
5.1 实现用户登陆逻辑, 新增--ihome/static/js/ihome/login.js
        post请求，获取参数request.get_json()
        判断获取结果是否存在
        获取详细参数mobile,password
        检验参数完整性
        校验手机号格式
        查询数据库，判断用户是否已注册或密码是否正确
        缓存用户信息，user_id,mobile,name
        返回结果，传递数据user_id--restful风格

5.2 实现获取用户基本信息逻辑，新增--ihome/static/js/ihome/my.js
        添加用户登录认证装饰器，获取参数user_id
        get请求无参数
        根据user_id查询数据库
        校验查询结果
        返回结果，传递参数user.to_dict()

5.3 实现修改用户信息逻辑，新增--ihome/static/js/ihome/profile.js
        添加用户登陆认证装饰器，获取参数user_id
        put请求获取参数request.get_json()
        判断获取结果是否存在
        获取详细参数name
        查询数据库，执行update命令更新用户信息
        提交session
        更新缓存中的用户信息
        返回结果，传递数据name-restful风格

5.4 实现上传用户头像逻辑
        添加用户登陆认证装饰器，获取参数user_id
        post请求获取参数request.files.get("avatar")
        读取图片文件中的数据
        调用七牛云接口，上传用户头像
        保存上传的结果--图片文件名，七牛云会对图片文件名进行编码处理
        查询数据库，保存用户头像
        拼接图片绝对路径
        返回结果，传递数据image_url-restful风格
5.5 实现用户实名认证逻辑，新增--ihome/static/js/ihome/auth.js
       添加用户登陆认证装饰器，获取参数user_id
       post请求获取参数request.get_json()
        判断参数是否存在
        获取详细参数real_name,id_card
        检验参数完整性
        把用户实名信息写入数据库，确保只执行第一次
        返回结果
5.6 实现获取用户实名信息逻辑
        添加用户登陆认证装饰器，获取参数user_id
        查询数据库，判断用户是否存在
        返回结果，传输数据user.auth_to_dict()


#### 6. 实现house.py中的逻辑，在ihome/api_1_0/__init__.py中导入house模块\
6.1 实现获取城区信息逻辑，新增--ihome/static/js/ihome/index.js
        尝试从redis中获取城区信息
        判断查询结果是否有数据
            有数据，留下访问redis数据库的日志记录
            返回结果
        查询mysql数据库
        判断查询结果
        定义空列表，存放查询结果
        遍历查询结果，将对象转化成字典存储在列表中
        序列化列表，转换成json
        存入redis缓存
        返回结果
6.2 实现发布新房源逻辑,新增--ihome/static/js/ihome/myhouse.js及newhouse.js
        添加用户登陆认证装饰器，获取参数user_id
        post获取参数,request.get_json()
        判断参数是否存在
        获取详细参数信息，不含配套设施
        检验参数完整性
        队加个参数进行转换，元-->分
        构造模型类对象，准备存储数据
        获取配套设施参数
        判断配套设施的存在
        对配套设施进行过滤查询，保证后端只存储数据库中已经定义的配套设施信息
        保存数据到mysql数据库
        返回结果，传输数据house_id,后面上传房屋图片时，前段可获取到house_id进行关联



获取城区信息
新建house.py

发布新房源

上传房屋图片


