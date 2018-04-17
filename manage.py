#coding=utf-8
from flask import session

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from iHome import get_app


#使用工厂模式
app = get_app('pro')
#将manager配置成Manager的对象
manager = Manager(app)

#在迁移是让app和db建立关联
# Migrate(app,db)
#将迁移脚本添加到脚本管理器
manager.add_command('db',MigrateCommand)


@app.route("/",methods=["GET","POST"])
def index():
    session['name'] = 'zsy'

    return "index"


if __name__ == '__main__':
    manager.run()