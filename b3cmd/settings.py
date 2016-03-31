import os
import re
from ConfigParser import ConfigParser

from fabric import api
from fabric import state

config = ConfigParser()
config.read([os.path.expanduser('~/.b3cmd.ini'), '/etc/b3cmd/b3cmd.ini'])
config_sections = config.sections()

default_branch = 'master'
default_project_name = os.path.basename(os.getcwd())
default_git_url = None
default_revision = None

git_head = './.git/HEAD'
try:
    with open(git_head) as f:
        data = f.read().strip()
        if 'refs/' in data:
            default_branch = data.split('/')[-1:][0]

    del data
    del git_head
except BaseException:
    pass

if os.getenv('GITLAB_CI') == 'true':
    default_branch = os.getenv('CI_BUILD_REF_NAME')
    default_git_url = os.getenv('CI_BUILD_REPO')
    default_revision = os.getenv('CI_BUILD_REF')

    finder = re.compile(r'([^/]+)\.git$')
    default_project_name = finder.search(default_git_url).group(1)

    del finder


def get_config_var(
    kwargs=None,
    kwarg_name=None,
    ini_name=None,
    env_name=None,
    default=None
):
    ret_env = None
    ret_ini = None
    ret_cli = None

    if env_name:
        ret_env = os.getenv(env_name)

    if ini_name:
        if '*' in config_sections:
            try:
                ret_ini = config.get('*', ini_name)
            except BaseException:
                pass

            ssh_host = api.env.get('ssh_host')
            if ssh_host:
                try:
                    ret_ini = config.get(ssh_host, ini_name)
                except BaseException:
                    pass

    if kwargs and kwarg_name:
        ret_cli = kwargs.get(kwarg_name)

    return ret_cli or ret_ini or ret_env or default


def init(*args, **kwargs):
    state.output.stdout = kwargs.get('verbose')
    api.env.output_prefix = False

    api.env.ssh_host = get_config_var(
        kwargs,
        kwarg_name='ssh_host',
        ini_name='ssh_host',
        env_name='B3CMD_SSH_HOST'
    )
    if not api.env.ssh_host:
        raise Exception('''
No SSH host set. Please do one of:
- Use `b3cmd --ssh-host`
- Set `ssh_host` in ~/.b3cmd.ini
- Set the `B3CMD_SSH_HOST` environment variable
        '''.strip())

    api.env.ssh_user = get_config_var(
        kwargs,
        kwarg_name='ssh_user',
        ini_name='ssh_user',
        env_name='B3CMD_SSH_USER',
        default='b3cmd'
    )

    api.env.ssh_port = get_config_var(
        kwargs,
        kwarg_name='ssh_port',
        ini_name='ssh_port',
        env_name='B3CMD_SSH_PORT',
        default=2224
    )

    api.env.project_name = get_config_var(
        kwargs,
        kwarg_name='project',
        env_name='B3CMD_PROJECT',
        default=default_project_name
    )

    api.env.branch = get_config_var(
        kwargs,
        kwarg_name='branch',
        env_name='B3CMD_BRANCH',
        default=default_branch
    )

    api.env.git_url = get_config_var(
        kwargs,
        kwarg_name='git_url',
        default=default_git_url
    )

    api.env.revision = get_config_var(
        env_name='B3CMD_REVISION',
        default=default_revision
    )

    api.env.docker_compose_alt_name = get_config_var(
        ini_name='docker_compose_alt_name',
        env_name='B3CMD_DOCKER_COMPOSE_ALT_NAME',
        default='docker-compose-alt.yml'
    )

    api.env.put_excludes = get_config_var(
        ini_name='put_excludes',
        default=(
            '.DS_Store',
            '.git/',
            '.svn/',
            '*.pyc',
        )
    )

    api.env.virtual_host_custom = get_config_var(
        kwargs,
        kwarg_name='virtual_host'
    )

    api.env.virtual_host_simple = get_config_var(
        kwargs,
        kwarg_name='virtual_host'
    )

    api.env.host_string = '%(ssh_host)s:%(ssh_port)s' % api.env

    if api.env.get('ssh_user'):
        api.env.host_string = '%(ssh_user)s@%(host_string)s' % api.env
