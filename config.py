#coding=utf-8
import redis


class Config(object):
    """封装配置的类"""
    DEBUG = True
    # mysql连接配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome'
    # mysql禁⽌止追踪数据库增删改
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis数据库配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    #秘钥
    SECRET_KEY = 'q6pBNcWPgmF6BqB6b5VICF7z7pI+90o0O4CaJsFGjzRsYiya9SEgUDytXvzFsIaR'

    # 指定存储session数据的数据库类型为redis
    SESSION_TYPE = 'redis'
    # 指定session数据存储到的位置
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 开启session数据的签名、混淆
    SESSION_USE_SIGNER = True
    # 设置session有效期:这里里里指的是session的扩展操作session时设置的有效期
    PERMANENT_SESSION_LIFETIME = 3600 * 24   # 一一天



class Develoment(Config):
    """开发模式下的配置"""
    pass


class Production(Config):
    """生产环境"""
    DEBUG = False
    PERMANENT_SESSION_LIFETIME = 3600 * 24 *2  # 一一天
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome_GZ'


class UnitTest(Config):
    """测试环境"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome_GZ_UnitTest'

#创建工厂原材料
configs = {
    'dev':Develoment,
    'pro':Production,
    'test':UnitTest,
}