# -*- coding:utf-8 -*-
from flask import Blueprint,current_app

#创建静态html文件蓝图
from flask import make_response
from flask_wtf.csrf import generate_csrf

html_blue = Blueprint('html',__name__)



#需求1:http://127.0.0.1:5000/register.html
#需求1:http://127.0.0.1:5000/===>默认加载index.html
#需求1:http://127.0.0.1:5000/favicon.ico
#创建静态html文件蓝图
@html_blue.route("/<re('.*'):file_name>")
def get_static_html(file_name):
    """提供静态html文件"""
    if not file_name:
        #实现只有根路径时，默认加载index.html
        file_name = 'index.html'

    if file_name != 'favicon.ico':
        file_name = 'html/%s' % file_name


    #创建响应对象
    response = make_response(current_app.send_static_file(file_name))
    #生成csrf_token
    csrf_token = generate_csrf()
    #将csrf_token写入到cookie
    response.set_cookie('csrf_token',csrf_token)



    #根据file_name拼接的全路径，去项目路径中查找静态html文件，并响应给浏览器
    # return current_app.send_static_file(file_name)
    return response
