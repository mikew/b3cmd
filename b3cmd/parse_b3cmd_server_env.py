from fabric import api
from fabric.contrib import files
from b3cmd.tasks.status import split_lines
import re


def parse_b3cmd_server_env():
    var_regex = r'^([a-zA-Z0-9_]+)=[\'"]?([^\'"]+)[\'"]?$'
    with api.hide('everything'):
        server_env = {}
        if files.exists('~/data/server_env'):
            for line in split_lines(api.run('cat ~/data/server_env')):
                match = re.match(var_regex, line)
                if not match:
                    continue

                var_name = match.group(1)
                var_value = match.group(2)
                server_env[var_name] = var_value

        api.env.b3cmd_root_template = server_env.get('B3CMD_HOST_PWD')
        api.env.virtual_host_template = server_env.get('B3CMD_VIRTUAL_HOST_TEMPLATE')
        api.env.git_url_template = server_env.get('B3CMD_GIT_TEMPLATE')
        api.env.namespace_from_server = server_env.get('B3CMD_DEFAULT_NAMESPACE')
