# b3cmd

CLI to manage internal S3+Heroku clone.

Can create application servers (projects containing either
`docker-compose.yml` or `docker-compose-alt.yml`). Will replace
`__VIRTUAL_HOST__` with `$PROJECT_NAME--$BRANCH.example.com`.

Can create static servers. Their `VIRTUAL_HOST` will be set to
`$PROJECT_NAME--$BRANCH--static.example.com`.

Unless otherwise given, the `$PROJECT_NAME` will be inferred from the
current directory. **Make sure you set this in CI**.

## Installation

```bash
pip install --upgrade git+https://github.com/mikew/b3cmd.git
```

## Usage

```bash
$ b3cmd
Usage: b3cmd [OPTIONS] COMMAND [ARGS]...

Options:
  --version                       Show the version and exit.
  --ssh-host TEXT                 The host to connect to. [$B3CMD_SSH_HOST]
  --ssh-port INTEGER              Default: 2224. [$B3CMD_SSH_PORT]
  --ssh-user TEXT                 Default: b3cmd. [$B3CMD_SSH_USER]
  --project TEXT                  Default: $(basename $PWD). [$B3CMD_PROJECT]
  --branch TEXT                   The git branch to use. [$B3CMD_BRANCH]
  --git-url TEXT                  Explicitly set the URL for git to clone.
  -v, --verbose / --no-verbose    Be verbose.
  --virtual-host TEXT             USE AT OWN RISK. Set a custom virtual host
                                  name.
  --simple-virtual-host / --no-simple-virtual-host
                                  USE AT OWN RISK. Set the virtual host name
                                  to just the project.
  -h, --help                      Show this message and exit.

Commands:
  all-rm                 Remove all servers for a project.
  all-status             See status of all projects.
  all-stop               Stop all servers.
  server-logs            Tail server logs.
  server-ps              See running containers.
  server-put             Copy files to server root via rsync.
  server-rm              Remove server servers.
  server-run             Run a command in a container.
  server-scaffold        Pull and run a project via docker-compose.
  server-scale           See `docker-compose scale --help`.
  server-stop            Stop containers for a project.
  static-ps              See running containers.
  static-put             Copy files to static root via rsync.
  static-rm              Remove static servers.
  static-scaffold        Create static server.
  static-scale           See `docker-compose scale --help`.
  static-stop            Stop static containers.
  static-unlink          Unlink (remove) a file.
  util-pgdump            Dump a Postgres container.
  util-pgrestore         Restore a Postgres dump.
  util-rethinkdbdump     Dump a Postgres container.
  util-rethinkdbrestore  Restore a RethinkDB dump.
```

## Examples

- Create a server and run a command on it:

  ```bash
  b3cmd server-scaffold
  b3cmd server-run web -- python manage.py migrate --noinput
  ```

- Get a database dump and restore it

  ```bash
  b3cmd util-pgdump myapp_db_1
  b3cmd util-pgrestore myapp_db_1 myapp_db_1.dump
  ```

- Copy static files and start a static server

  ```bash
  b3cmd static-put public/ /
  ```
