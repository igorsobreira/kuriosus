import os
from fabric.api import *

env.hosts = ['igor@igorsobreira.com']

virtualenv_dir = '/home/igor/learning_env'
project_dir = virtualenv_dir + '/reading'
logfile = virtualenv_dir + '/twistd.log'
pidfile = virtualenv_dir + '/twistd.pid'

def deploy():
    local("tar -czf /tmp/kuriosus-package.tgz "
          "--exclude=tests --exclude=.git --exclude=_trial_temp --exclude=*.pyc .")
    put('/tmp/kuriosus-package.tgz', '/tmp/')
    run('mkdir -p %s' % project_dir)
    with cd(project_dir):
        run('tar pxzvf /tmp/kuriosus-package.tgz')
        run('../bin/pip install -r requirements.txt')

def start():
    with cd(project_dir):
        run('../bin/twistd --logfile=%s --pidfile=%s --python=kuriosus/main.tac'
            % (logfile, pidfile))

def stop():
    run("if [ -f %(pidfile)s ]; then kill `cat %(pidfile)s`; fi"
        % {'pidfile':pidfile})

def log():
    run('tail -f %s' % logfile)
