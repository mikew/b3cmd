if not __package__:
    from os import sys, getcwd
    cwd = getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

import click
from b3cmd import settings
from b3cmd.parse_b3cmd_server_env import parse_b3cmd_server_env
from b3cmd.version import __version_string__
from b3cmd.fabric_execute import fabric_execute
from b3cmd.tasks import (
    postgres,
    server,
    static,
    status,
    rethinkdb,
)

CLICK_CONTEXT_SETTINGS = {
    'help_option_names': ('-h', '--help'),
}


@click.group(context_settings=CLICK_CONTEXT_SETTINGS)
@click.version_option(version=__version_string__)
@click.option('--ssh-host', help='The host to connect to. [$B3CMD_SSH_HOST]')
@click.option('--ssh-port', type=int, help='Default: 2224. [$B3CMD_SSH_PORT]')
@click.option('--ssh-user', help='Default: b3cmd. [$B3CMD_SSH_USER]')
@click.option('--project', help='Default: $(basename $PWD). [$B3CMD_PROJECT]')
@click.option('--branch', help='The git branch to use. [$B3CMD_BRANCH]')
@click.option('--namespace', help='The namespace to use. [$B3CMD_NAMESPACE]')
@click.option('--git-url', help='Explicitly set the URL for git to clone.')
@click.option('--verbose/--no-verbose', '-v', help='Be verbose.')
@click.option('--virtual-host', help='USE AT OWN RISK. Set a custom virtual host name.')
@click.option('--simple-virtual-host/--no-simple-virtual-host', help='USE AT OWN RISK. Set the virtual host name to just the project.')
def main(*args, **kwargs):
    settings.init(*args, **kwargs)
    parse_b3cmd_server_env()
    settings.finalize()


@main.command(name='server-scaffold', help='Pull and run a project via docker-compose.')
@click.option('--revision', help='Revision or branch to deploy. [$B3CMD_REVISION]')
def server_scaffold(*args, **kwargs):
    fabric_execute(server.server_scaffold, *args, **kwargs)


@main.command(name='server-stop', help='Stop containers for a project.')
def server_stop():
    fabric_execute(server.server_stop)


@main.command(name='server-run', help='Run a command in a container.')
@click.argument('container_name')
@click.argument('command', nargs=-1)
def server_run(*args, **kwargs):
    fabric_execute(server.server_run, *args, **kwargs)


@main.command(name='server-put', help='Copy files to server root via rsync.')
@click.argument('local_path')
@click.argument('remote_path')
def server_put(*args, **kwargs):
    fabric_execute(server.server_put, *args, **kwargs)


@main.command(name='server-logs', help='Tail server logs.')
@click.option('--timestamps/--no-timestamps', '-t', help='Show timestamps')
@click.option('--follow/--no-follow', '-f', default=True, help='Follow')
@click.option('--tail', default='200', help='Number of lines to show from the end of the logs for each container')
@click.argument('container_name', nargs=1, required=False)
def server_logs(*args, **kwargs):
    fabric_execute(server.server_logs, *args, **kwargs)


@main.command(name='server-scale', help='See `docker-compose scale --help`.')
@click.argument('services', nargs=-1)
def server_scale(*args, **kwargs):
    if len(kwargs.get('services')) is 0:
        raise click.BadOptionUsage('services', '%s option requires at least 1 arguments.' % 'services')
    fabric_execute(server.server_scale, *args, **kwargs)


@main.command(name='server-ps', help='See running containers.')
def server_ps():
    fabric_execute(server.server_ps)


@main.command(name='static-scaffold', help='Create static server.')
def static_scaffold():
    fabric_execute(static.static_scaffold)


@main.command(name='static-stop', help='Stop static containers.')
def static_stop():
    fabric_execute(static.static_stop)


@main.command(name='static-put', help='Copy files to static root via rsync.')
@click.argument('local_path')
@click.argument('remote_path')
def static_put(*args, **kwargs):
    fabric_execute(static.static_put, *args, **kwargs)


@main.command(name='all-stop', help='Stop all servers.')
@click.pass_context
def all_stop(ctx):
    ctx.invoke(server_stop)
    ctx.invoke(static_stop)


def click_deny_callback(ctx, param, value):
    if not value:
        ctx.abort()


@main.command(name='static-rm', help='Remove static servers.')
@click.option('--force/--no-force', '-f', callback=click_deny_callback,
              expose_value=False, prompt='Do you want to continue?')
def static_rm():
    fabric_execute(static.static_rm)


@main.command(name='server-rm', help='Remove server servers.')
@click.option('--force/--no-force', '-f', callback=click_deny_callback,
              expose_value=False, prompt='Do you want to continue?')
def server_rm():
    fabric_execute(server.server_rm)


@main.command(name='all-rm', help='Remove all servers for a project.')
@click.pass_context
@click.option('--force/--no-force', '-f', callback=click_deny_callback,
              expose_value=False, prompt='Do you want to continue?')
def all_rm(ctx):
    ctx.invoke(server_rm)
    ctx.invoke(static_rm)


@main.command(name='static-unlink', help='Unlink (remove) a file.')
@click.option('--recursive/--no-recursive', '-r', help='Make recursive.')
@click.option('--force/--no-force', '-f', help='Force.')
@click.option('--dry-run/--no-dry-run', '-n', help='Dry run.')
@click.argument('paths', nargs=-1)
def static_unlink(*args, **kwargs):
    if len(kwargs.get('paths')) is 0:
        raise click.BadOptionUsage('paths', '%s option requires at least 1 arguments.' % 'paths')

    fabric_execute(static.static_unlink, *args, **kwargs)


@main.command(name='static-scale', help='See `docker-compose scale --help`.')
@click.argument('services', nargs=-1)
def static_scale(*args, **kwargs):
    if len(kwargs.get('services')) is 0:
        raise click.BadOptionUsage('services', '%s option requires at least 1 arguments.' % 'services')
    fabric_execute(static.static_scale, *args, **kwargs)


@main.command(name='static-ps', help='See running containers.')
def static_ps():
    fabric_execute(static.static_ps)


@main.command('all-status', help='See status of all projects.')
@click.option('--color/--no-color', default=True, help='Use color to show up / down status.')
def all_status(*args, **kwargs):
    fabric_execute(status.all_status, *args, **kwargs)


@main.command('util-pgrestore', help='Restore a Postgres dump.')
@click.option('--dbuser')
@click.option('--dbpass')
@click.option('--dbhost')
@click.option('--dbname')
@click.option('--dbport')
@click.argument('container_name')
@click.argument('local_path')
def util_pgrestore(*args, **kwargs):
    fabric_execute(postgres.pgrestore, *args, **kwargs)


@main.command('util-pgdump', help='Dump a Postgres container.')
@click.option('--dbuser')
@click.option('--dbpass')
@click.option('--dbhost')
@click.option('--dbname')
@click.option('--dbport')
@click.argument('container_name')
def util_pgdump(*args, **kwargs):
    fabric_execute(postgres.pgdump, *args, **kwargs)


@main.command('util-rethinkdbrestore', help='Restore a RethinkDB dump.')
@click.option('--auth')
@click.argument('container_name')
@click.argument('local_path')
def util_rethinkdbrestore(*args, **kwargs):
    fabric_execute(rethinkdb.dump, *args, **kwargs)


@main.command('util-rethinkdbdump', help='Dump a Postgres container.')
@click.option('--auth')
@click.argument('container_name')
def util_rethinkdbdump(*args, **kwargs):
    fabric_execute(rethinkdb.restore, *args, **kwargs)


if __name__ == '__main__':
    main()
