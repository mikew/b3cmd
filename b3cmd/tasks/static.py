import re
from fabric import api
from b3cmd.get_virtual_host import get_virtual_host
from b3cmd.sanitize_remote_path import sanitize_remote_path
from fabric.contrib.project import rsync_project


@api.runs_once
def setup_env():
    unique_host_name = '%(project_name)s--%(branch)s--static' % api.env
    api.env.project_path = '%(b3cmd_root_template)s/%(namespace)s--%(project_name)s--%(branch)s--static' % (api.env)
    api.env.project_host_name = get_virtual_host(unique_host_name)
    api.env.virtual_host = api.env.virtual_host_template % api.env


def static_scaffold():
    setup_env()

    if api.run('[ -d "%(project_path)s" ]' % api.env, quiet=True).return_code == 1:
        api.run('mkdir -p "%(project_path)s"' % api.env)

    with api.cd(api.env.project_path):
        api.run('''
cat <<-EOF > docker-compose.yml
main:
  image: nginx
  environment:
    - VIRTUAL_HOST=%(virtual_host)s
    - CORS_ENABLED=true
  volumes:
    - .:/usr/share/nginx/html
EOF
''' % api.env)

        api.run('docker-compose pull')
        static_stop()
        api.run('docker-compose up -d')


def static_stop():
    setup_env()

    with api.warn_only():
        with api.cd(api.env.project_path):
            api.run('docker-compose stop' % api.env)


def static_put(local_path, remote_path):
    setup_env()

    static_scaffold()
    remote_path = sanitize_remote_path(remote_path)
    rsync_project(
        exclude=api.env.put_excludes,
        local_dir=local_path,
        remote_dir='%s/%s' % (api.env.project_path, remote_path),
        extra_opts='--chmod=a=r,u+w,D+x'
    )


def static_rm():
    setup_env()
    static_stop()
    with api.warn_only():
        with api.cd(api.env.project_path):
            api.run('docker-compose rm -f -v')


def static_unlink(paths, force, recursive, dry_run):
    setup_env()

    paths_joined = ''
    paths = tuple(sanitize_remote_path(path) for path in paths)
    for path in paths:
        if not path:
            raise Exception('`%s` is not a valid path' % path)

        if '*' in path:
            paths_joined += ' %s' % path
        else:
            paths_joined += ' "%s"' % path

    if dry_run:
        cmd = 'ls'
    else:
        cmd = 'rm'

        if force:
            cmd = '%s -f' % cmd

    if recursive:
        cmd = '%s -r' % cmd

    with api.cd(api.env.project_path):
        api.run('%s %s' % (cmd, paths_joined))


def static_scale(services):
    setup_env()
    api.env.services = ' '.join(services)
    if '=' in api.env.services:
        api.env.services = re.sub(r'.*=(\d+).*', r'\1', api.env.services)
        print 'Static servers only have one service, you can just pass a number'

    with api.cd(api.env.project_path):
        api.run('docker-compose scale main=%(services)s' % api.env)


def static_ps():
    setup_env()
    with api.settings(api.hide('everything'), api.show('stdout')):
        with api.cd(api.env.project_path):
            api.run('docker-compose ps')
