from fabric import api
from fabric.contrib import files
from b3cmd.get_virtual_host import get_virtual_host
from b3cmd.sanitize_remote_path import sanitize_remote_path
from fabric.contrib.project import rsync_project


def find_docker_compose_file():
    api.env.docker_compose_file = 'docker-compose.yml'
    with api.cd(api.env.project_path):
        if files.exists(api.env.docker_compose_alt_name):
            api.env.docker_compose_file = api.env.docker_compose_alt_name


@api.runs_once
def setup_env():
    unique_host_name = '%(project_name)s--%(branch)s' % api.env
    api.env.project_host_name = get_virtual_host(unique_host_name)
    api.env.virtual_host = api.env.virtual_host_template % api.env
    api.env.project_path = '%s/%s' % (api.env.b3cmd_root_template, unique_host_name)

    find_docker_compose_file()


def server_scaffold(revision=None):
    setup_env()
    if not api.env.get('namespace'):
        api.env.namespace = api.env.get('default_namespace')

    if not api.env.get('git_url'):
        api.env.git_url = api.env.git_url_template % api.env.project_name

    if not revision:
        revision = "origin/%(branch)s" % api.env

    if not files.exists('%(project_path)s/.git' % api.env):
        api.run('mkdir -p %(project_path)s' % api.env)
        with api.cd(api.env.project_path):
            api.run('git init .')
            api.run('git remote add -t \* -f origin %(git_url)s' % api.env)
            # api.run('git clone "%(git_url)s" .' % api.env)

    with api.cd(api.env.project_path):
        api.run('git checkout -- "%(docker_compose_file)s"' % api.env, warn_only=True)
        api.run('git fetch origin')
        api.run('git checkout "%s"' % revision)

        find_docker_compose_file()
        api.run('''
sed -i -E \
    -e "s/__HOST__/%(project_host_name)s/g" \
    -e "s/__PROJECT__/%(project_name)s/g" \
    -e "s/__BRANCH__/%(branch)s/g" \
    -e "s/__VIRTUAL_HOST__/%(virtual_host)s/g" \
    "%(docker_compose_file)s"
''' % api.env)
        # api.run('sed -i -E "s/__HOST__/%(project_host_name)s/" "%(docker_compose_file)s"' % api.env)
        # api.run('sed -i -E "s/__BRANCH__/%(branch)s/" "%(docker_compose_file)s"' % api.env)
        api.run('docker-compose -f "%(docker_compose_file)s" pull' % api.env)
        api.run('docker-compose -f "%(docker_compose_file)s" build --pull' % api.env)
        server_stop()
        api.run('docker-compose -f "%(docker_compose_file)s" up -d' % api.env)


def server_stop():
    setup_env()

    with api.warn_only():
        with api.cd(api.env.project_path):
            api.run('docker-compose -f "%(docker_compose_file)s" stop' % api.env)


def server_run(container_name, command):
    setup_env()
    api.env.container_name = container_name
    api.env.command = ' '.join(command)

    with api.settings(api.show('output')):
        with api.cd(api.env.project_path):
            api.run('docker-compose -f "%(docker_compose_file)s" run --rm "%(container_name)s" %(command)s' % api.env)


def server_logs():
    setup_env()

    with api.cd(api.env.project_path):
        api.run('docker-compose -f "%(docker_compose_file)s" logs' % api.env)


def server_put(local_path, remote_path):
    setup_env()

    remote_path = sanitize_remote_path(remote_path)
    api.run('mkdir -p %(project_path)s' % api.env)
    rsync_project(
        exclude=api.env.put_excludes,
        local_dir=local_path,
        remote_dir='%s/%s' % (api.env.project_path, remote_path)
    )


def server_rm():
    setup_env()
    server_stop()
    with api.warn_only():
        with api.cd(api.env.project_path):
            api.run('docker-compose -f "%(docker_compose_file)s" rm -f -v' % api.env)


def server_scale(services):
    setup_env()
    api.env.services = ' '.join(services)
    with api.cd(api.env.project_path):
        api.run('docker-compose -f "%(docker_compose_file)s" scale %(services)s' % api.env)


def server_ps():
    setup_env()
    with api.settings(api.hide('everything'), api.show('stdout')):
        with api.cd(api.env.project_path):
            api.run('docker-compose -f "%(docker_compose_file)s" ps' % api.env)
