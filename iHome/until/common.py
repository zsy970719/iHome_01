# -*- coding:utf-8 -*-
#定义公共的工具文件
from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    #自定义路由转换器
    def __init__(self,url_map,*args):
        super(RegexConverter,self).__init__(url_map)
        #保存正则
        self.regex = args[0]
