#coding=utf-8

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from iHome import get_app,db
from iHome import models    #没有实际意义，只在迁移前告知迁移脚本，有哪些模型类

#用工厂模式创建app
app = get_app('dev')

#将manager配置成Manager的对象
manager = Manager(app)

#在迁移是让app和db建立关联
Migrate(app,db)
#将迁移脚本添加到脚本管理器
manager.add_command('db',MigrateCommand)




if __name__ == '__main__':
    print app.url_map
    manager.run()