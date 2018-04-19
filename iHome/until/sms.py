#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

#���ʺ�
accountSid= '8a216da862dcd1050162ddcf1eb50101'

#���ʺ�Token
accountToken= '5c4fe24b056c4d23adc217979b6f5c5e'

#Ӧ��Id
appId='8a216da862dcd1050162ddcf1f170108'

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

#����˿� 
serverPort='8883'

#REST�汾��
softVersion='2013-12-26'


class CCP(object):
    """��װ�����࣬����ͳһ�ķ��Ͷ�����֤��"""
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)

            # ��ʼ��REST SDK
            cls._instance.rest = REST(serverIP, serverPort, softVersion)
            cls._instance.rest.setAccount(accountSid, accountToken)
            cls._instance.rest.setAppId(appId)

        return cls._instance


    def send_sms_code(self, to, datas, tempId):
        """���Ͷ�����֤���ʵ������"""

        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # �жϷ��Ͷ����Ƿ�ɹ�
        if result.get('statusCode') == '000000':
            # ����ķ���ֵ�Ǹ��������жϷ��Ͷ����Ƿ�ɹ���
            return 1
        else:
            return 0


# ����ģ�����
# @param to �ֻ�����
# @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
# @param $tempId ģ��Id
# def sendTemplateSMS(to,datas,tempId):
#
#
#     #��ʼ��REST SDK
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
# # ��17600992168���Ͷ�����֤�룬����Ϊ666666��5���Ӻ���ڣ�ʹ��idΪ1��ģ��
# sendTemplateSMS('15579857087', ['666666', '5'], '1')