# -*- coding:utf-8 -*-
# 上传、保存图片到七牛云


import qiniu


access_key = 'yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW'
secret_key = 'bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW'
bucket_name = 'ihome'


def upload_image(image_data):
    """上传、保存图片到七牛云"""

    # 创建七牛云对象
    q = qiniu.Auth(access_key, secret_key)
    # 获取上传的token
    token = q.upload_token(bucket_name)
    # 调用上传的方法，实现生产并响应结果给我们
    # 说明：参数2传入None,表示让七牛云给我们生成数据的唯一标识key
    ret, info = qiniu.put_data(token, None, image_data)

    # 判断上传图片是否成功
    if info.status_code == 200:
        key = ret.get('key')
        return key
    else:
        raise Exception('上传图片失败')