from fabric import api


def dump(container_name, local_path, auth=None):
    api.env.container_name = container_name
    api.env.auth = auth or ''

    with api.settings(api.hide('everything')):
        api.env.workdir = api.run('mktemp -d -p %(b3cmd_root_template)s -t b3cmd_util_rethinkdbrestore.XXXXXXXX' % api.env)
        api.put(
            local_path=local_path,
            remote_path='%(workdir)s/database.tar.gz' % api.env
        )

        api.run('''
cd "%(workdir)s"

cat <<-EOF > b3cmd-rethinkdbrestore
#!/usr/bin/env bash
DB_AUTH="%(auth)s"
DUMPFILE="/b3cmd_util_rethinkdbrestore/database.tar.gz"

rethinkdb restore \
    "\\\$DUMPFILE"
    --connect \\\$DB_PORT_28015_TCP_ADDR:\\\$DB_PORT_28015_TCP_PORT \
    --auth "\\\$DB_AUTH" \
chown $UID:$GROUPS "\\\$DUMPFILE"
EOF
chmod +x b3cmd-rethinkdbrestore

docker run --rm \
    --link "%(container_name)s:db" \
    --volume $(pwd):/b3cmd_util_rethinkdbrestore \
    mikewhy/rethinkdb-py \
    /b3cmd_util_rethinkdbrestore/b3cmd-rethinkdbrestore
''' % api.env)

    api.run('rm -r %(workdir)s' % api.env)


def restore(container_name, auth=None):
    api.env.container_name = container_name
    api.env.auth = auth or ''

    with api.settings(api.hide('everything')):
        api.env.workdir = api.run('mktemp -d -p %(b3cmd_root_template)s -t b3cmd_util_rethinkdbdump.XXXXXXXX' % api.env)

        api.run('''
cd "%(workdir)s"

cat <<-EOF > b3cmd-rethinkdbdump
#!/usr/bin/env bash
DB_AUTH="%(auth)s"
DUMPFILE="/b3cmd_util_rethinkdbdump/%(container_name)s.tar.gz"

rethinkdb dump \
    --connect \\\$DB_PORT_28015_TCP_ADDR:\\\$DB_PORT_28015_TCP_PORT \
    --auth "\\\$DB_AUTH" \
    --file "\\\$DUMPFILE"
chown $UID:$GROUPS "\\\$DUMPFILE"
EOF
chmod +x b3cmd-rethinkdbdump

docker run --rm \
    --link "%(container_name)s:db" \
    --volume $(pwd):/b3cmd_util_rethinkdbdump \
    mikewhy/rethinkdb-py \
    /b3cmd_util_rethinkdbdump/b3cmd-rethinkdbdump
''' % api.env)

    api.get(
        remote_path='%(workdir)s/%(container_name)s.tar.gz' % api.env,
        local_path='%(container_name)s.tar.gz' % api.env
    )
    api.run('rm -r %(workdir)s' % api.env)
