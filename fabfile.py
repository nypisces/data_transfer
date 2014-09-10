# -*- coding: utf-8 -*-

from contextlib import contextmanager
import os

from fabric.colors import red, green, yellow, blue, magenta, cyan
from fabric.context_managers import cd, hide, prefix, settings, lcd, path
from fabric.contrib.files import exists
from fabric.decorators import task, roles, parallel
from fabric.operations import local, run, sudo, put, get
from fabric.state import env
from fabric.tasks import execute
from fabric.utils import puts


# ===========
# = GLOBALS =
# ===========
env.project_name = os.path.basename(os.path.dirname(__file__))
env.project_path = '~/GitHub/{}'.format(env.project_name)
# 手动配置
env.repository = 'git@github.com:finwise/{}.git'.format(env.project_name)
env.user = 'ubuntu'
env.key_filename = '~/key/06866com-aws-cn.pem'  # SSH 证书 / 密码
env.newrelic_key = '7cba721d377c66139fb07c29ecf1bae50e3dbf43'
# 其他
env.forward_agent = True  # GitHub的代理转发部署方式需要开启这项
env.colorize_errors = True
# 自定义
env.run = run


@task
def local_runserver():
    run("ps aux |grep redis_server.py |grep -v 'grep' | awk '{print $2}'|xargs kill -9")
    run("ps aux |grep send_sms.py |grep -v 'grep' | awk '{print $2}'|xargs kill -9")
    run('nohup /usr/bin/python3 {0}/apps/products/redis_server.py >/dev/null &'.format(env.project_path))
    run('nohup /usr/bin/python3 {0}/apps/products/send_sms.py >/dev/null &'.format(env.project_path))
    run('dos2unix {0}/monitor.sh'.format(env.project_path))


@task
def local_crontab():
    run("echo */15 * * * * /usr/bin/pytnon3 {0}/apps/products/distribution.py >>".format(env.project_path))


@contextmanager
def virtualenv():
    with prefix('workon {}'.format(env.project_name)):
        yield


@task
def prod():
    env.test = False
    env.roledefs = {  # 无论是否同一个role中，只要有重复的ip默认不执行
        'app': ['必填'],
        'redis': ['必填']
    }


@task
def test():
    env.test = True
    env.roledefs = {
        'app': ['54.223.140.206'],
        'redis': ['54.223.140.206']
    }


@task
def dev():
    env.run = local


# ============
# =  Hello   =
# ============
@task(default=True, alias='别名测试')
def hello():
    puts('*' * 50)
    puts(cyan('  Fabric 使用指南\n'))
    puts(green('  查看所有命令请输入: fab -l'))
    puts(yellow('  带参数命令请输入: fab 命令:参数'))
    puts(magenta('  手动配置env.(repository, key_filename, newrelic_key, roledefs)'))
    puts(blue('  部署正式环境: fab prod deplay'))
    puts('  Project Name: {}'.format(env.project_name))
    puts('*' * 50)


@task()
@roles('app')
def init_app():
#     apt_upgrade()
#     sudo('apt-get -y install libmysqlclient-dev python3-pip git tree')  # tree只是为了登陆服务器时查看方便 libjpeg8-dev libpng-dev libgif-dev
#     sudo('pip3 install -U virtualenvwrapper')
#     sudo('pip3 install git+https://github.com/Supervisor/supervisor.git')
#     put('configs/bashrc', '~/.bashrc')
    sputs('创建代码库')
    run('git clone {0.repository} {0.project_path}'.format(env))
    if env.test:
        smartrun('git checkout develop')
    run('mkvirtualenv {}'.format(env.project_name))  # 永远不要在virtualenv上用sudo


@task
@roles('redis')
def init_redis():
    sputs(yellow('● 开始部署'))
    sudo('apt-get -y install redis-server')
    sudo('/etc/init.d/redis-server start')
    sudo('apt-get -y install memcached')
    sudo('memcached -m 64 -l 127.0.0.1 -p 11211 -d')
    sputs(yellow('● 完成部署'))


@task
@roles('app')
def init_newrelic():
    sudo('echo deb http://apt.newrelic.com/debian/ newrelic non-free >> /etc/apt/sources.list.d/newrelic.list')
    sudo('wget -O- https://download.newrelic.com/548C16BF.gpg | apt-key add -')
    sudo('apt-get update')
    sudo('apt-get install -y newrelic-sysmond')
    sudo('nrsysmond-config --set license_key={}'.format(env.newrelic_key))
    sudo('/etc/init.d/newrelic-sysmond start')


# ============
# =  Deploy  =
# ============
def apt_upgrade():
    sputs(yellow('● ├── apt-get升级/安装'))
    sudo('apt-get -y update')
    sudo('apt-get -y upgrade')  # 为了稳定, 不要用dist-upgrade
    sudo('apt-get clean')


@task
def deploy(deploy_type='quick'):
    """部署到生产服务器"""
    with settings(
        # hide('stdout'),
        warn_only=False
    ):
        deploy_app()  # 就算只有一个地址，只要是roles('app')这样使用，就要放在execute内执行，否则取不到role


@task
@roles('app')
def deploy_app():
    # apt_upgrade()
    sputs(yellow('● 开始部署'))
    smartrun('git pull')
#    with cd(env.project_path), prefix('workon {}'.format(env.project_name)):
       # run('pip3 install -U -r requirements.txt')
#     if exists('/tmp/supervisor.sock'):
#         # supervisor_update()
#         supervisor_restart('gunicorn')
#     else:
#         supervisor_conf()
    local_runserver()
    sputs(yellow('● 完成部署'))
    puts('', show_prefix=False)


# ==================
# = Configurations =
# ==================
# Supervisor
# --------------------------------------------------------------------------------
def supervisor_conf():
    run('supervisord -c {}/etc/supervisord.conf'.format(env.project_path))  # 配置好gunicorn的directory之后任意目录运行都行


def supervisor_unlink():  # 停止supervisord
    run('unlink /tmp/supervisor.sock')


def supervisor_start(process='all'):  # 因为上面是进入目录执行的, 所以重启之类的也要进入目录执行
    smartrun('supervisorctl start {}'.format(process))


def supervisor_restart(process='all'):
    smartrun('supervisorctl restart {}'.format(process))


def supervisor_stop(process='all'):
    smartrun('supervisorctl stop {}'.format(process))


def supervisor_remove(process='all'):
    smartrun('supervisorctl remove {}'.format(process))


def supervisor_update():  # 更新配置文件
    smartrun('supervisorctl update')


# Redis
# --------------------------------------------------------------------------------
def start_redis():
    sudo('/etc/init.d/redis-server start')


def stop_redis():
    run('/etc/init.d/redis-server stop')


def restart_redis():
    run('/etc/init.d/redis-server restart')


def configure_redis():
    put('server_configs/{}/redis/redis.conf'.format(env.servername), '/etc/redis/', use_sudo=True)


# ============
# = 工具方法  =
# ============
def smartrun(command):
    with cd(env.project_path):
        run(command)


def sputs(text):
    if env.host_string in env.roledefs['app']:
        puts(text + green('【应用服务器】[{}]'.format(env.host_string) + yellow(' ==')), show_prefix=False)
    elif env.host_string in env.roledefs['db']:
        puts(text + cyan('【数据库服务器】[{}]'.format(env.host_string) + yellow(' ==')), show_prefix=False)
    elif env.host_string in env.roledefs['redis']:
        puts(text + red('【Redis服务器】[{}]'.format(env.host_string) + yellow(' ==')), show_prefix=False)
    else:
        puts(text + magenta('【未知类型服务器】[{}]'.format(env.host_string) + yellow(' =='), bold=True), show_prefix=False)
