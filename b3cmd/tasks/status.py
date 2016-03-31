from fabric import api
from fabric import colors
import re


def split_lines(output=''):
    return re.split(r"\r?\n", output)


def format_docker_compose_name(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())


def all_status(color=True):
    unique_host_name = '.'
    project_path = '%s/%s' % (api.env.b3cmd_root_template, unique_host_name)

    with api.settings(api.hide('everything')):
        with api.cd(project_path):
            all_running = split_lines(
                api.run('docker ps | tail -n+2 | rev | cut -d " " -f 1 | rev | cut -d "_" -f 1 | sort | uniq')
            )
            existing_projects = split_lines(
                api.run('find . -maxdepth 1 -type d | sort -f')
            )

            for p in existing_projects:
                if p == '.' or p == './':
                    continue

                p = p.replace('./', '', 1)
                is_running = format_docker_compose_name(p) in all_running
                parts = p.split('--')
                project_name = parts[0]
                branch = parts[1]
                try:
                    server_type = parts[2]
                except BaseException:
                    server_type = 'server'

                message = '--project %s --branch %s %s' % (project_name, branch, server_type)
                if is_running:
                    if color:
                        print colors.green(message)
                    else:
                        print 'UP: %s' % message
                else:
                    if color:
                        print colors.red(message)
                    else:
                        print 'DOWN: %s' % message
