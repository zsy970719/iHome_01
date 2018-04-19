#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

#主帐号
accountSid= '8a216da862dcd1050162ddcf1eb50101'

#主帐号Token
accountToken= '5c4fe24b056c4d23adc217979b6f5c5e'

#应用Id
appId='8a216da862dcd1050162ddcf1f170108'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'


class CCP(object):
    """封装单例类，用于统一的发送短信验证码"""
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)

            # 初始化REST SDK
            cls._instance.rest = REST(serverIP, serverPort, softVersion)
            cls._instance.rest.setAccount(accountSid, accountToken)
            cls._instance.rest.setAppId(appId)

        return cls._instance


    def send_sms_code(self, to, datas, tempId):
        """发送短信验证码的实例方法"""

        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # 判断发送短信是否成功
        if result.get('statusCode') == '000000':
            # 这里的返回值是给调用者判断发送短信是否成功的
            return 1
        else:
            return 0


# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id
# def sendTemplateSMS(to,datas,tempId):
#
#
#     #初始化REST SDK
#     rest = REST(serverIP,serverPort,softVersion)
#     rest.setAccount(accountSid,accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to,datas,tempId)
#     for k,v in result.iteritems():
#
#         if k=='templateSMS' :
#                 for k,s in v.iteritems():
#                     print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)
#
# # 向17600992168发送短信验证码，内容为666666，5分钟后过期，使用id为1的模板
# sendTemplateSMS('15579857087', ['666666', '5'], '1')