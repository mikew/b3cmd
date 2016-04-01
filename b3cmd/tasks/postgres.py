from fabric import api


def pgrestore(container_name, local_path, dbuser=None, dbpass=None, dbhost=None, dbname=None, dbport=None):
    api.env.container_name = container_name
    api.env.dbuser = dbuser or ''
    api.env.dbpass = dbpass or ''
    api.env.dbhost = dbhost or 'db'
    api.env.dbname = dbname or ''
    api.env.dbport = dbport or '5432'

    with api.settings(api.hide('everything')):
        api.env.workdir = api.run('mktemp -d -p %(b3cmd_root_template)s -t b3cmd_util_pgrestore.XXXXXXXX' % api.env)
        api.put(
            local_path=local_path,
            remote_path='%(workdir)s/database.dump' % api.env
        )

        api.run('''
cd "%(workdir)s"

cat <<-EOF > b3cmd-pgrestore
#!/usr/bin/env bash
DBUSER="%(dbuser)s"
DBPASS="%(dbpass)s"
DBHOST="%(dbhost)s"
DBNAME="%(dbname)s"
DBPORT="%(dbport)s"
DUMPFILE="/b3cmd_util_pgrestore/database.dump"

[ -z "\\\$DBUSER" ] && DBUSER="\\\$DB_ENV_POSTGRES_USER"
[ -z "\\\$DBPASS" ] && DBPASS="\\\$DB_ENV_POSTGRES_PASSWORD"
[ -z "\\\$DBPASS" ] && DBPASS="\\\$DB_ENV_POSTGRES_USER"
[ -z "\\\$DBNAME" ] && DBNAME="\\\$DB_ENV_POSTGRES_USER"

[ -n "\\\$DBPASS" ] && export PGPASSWORD="\\\$DBPASS"
pg_restore \
    --clean \
    --no-acl \
    --no-owner \
    --username "\\\$DBUSER" \
    --dbname "\\\$DBNAME" \
    --port "\\\$DBPORT" \
    --host "\\\$DBHOST" \
    "\\\$DUMPFILE"
EOF
chmod +x b3cmd-pgrestore

PG_MAJOR=$(docker exec "%(container_name)s" env | grep PG_MAJOR | cut -d = -f 2)
PG_MAJOR=${PG_MAJOR:-9.4}
docker run --rm \
    --link "%(container_name)s:db" \
    --volume $(pwd):/b3cmd_util_pgrestore \
    postgres:$PG_MAJOR \
    /b3cmd_util_pgrestore/b3cmd-pgrestore
''' % api.env)

    api.run('rm -r %(workdir)s' % api.env)


def pgdump(container_name, dbuser=None, dbpass=None, dbhost=None, dbname=None, dbport=None):
    api.env.container_name = container_name
    api.env.dbuser = dbuser or ''
    api.env.dbpass = dbpass or ''
    api.env.dbhost = dbhost or 'db'
    api.env.dbname = dbname or ''
    api.env.dbport = dbport or '5432'

    with api.settings(api.hide('everything')):
        api.env.workdir = api.run('mktemp -d -p %(b3cmd_root_template)s -t b3cmd_util_pgdump.XXXXXXXX' % api.env)

        api.run('''
cd "%(workdir)s"

cat <<-EOF > b3cmd-pgdump
#!/usr/bin/env bash
DBUSER="%(dbuser)s"
DBPASS="%(dbpass)s"
DBHOST="%(dbhost)s"
DBNAME="%(dbname)s"
DBPORT="%(dbport)s"
DUMPFILE="/b3cmd_util_pgdump/%(container_name)s.dump"

[ -z "\\\$DBUSER" ] && DBUSER="\\\$DB_ENV_POSTGRES_USER"
[ -z "\\\$DBPASS" ] && DBPASS="\\\$DB_ENV_POSTGRES_PASSWORD"
[ -z "\\\$DBPASS" ] && DBPASS="\\\$DB_ENV_POSTGRES_USER"
[ -z "\\\$DBNAME" ] && DBNAME="\\\$DB_ENV_POSTGRES_USER"

[ -n "\\\$DBPASS" ] && export PGPASSWORD="\\\$DBPASS"
pg_dump \
    --username "\\\$DBUSER" \
    --dbname "\\\$DBNAME" \
    --port "\\\$DBPORT" \
    --host "\\\$DBHOST" \
    --format custom \
    --compress 9 \
    --file "\\\$DUMPFILE"
chown $UID:$GROUPS "\\\$DUMPFILE"
EOF
chmod +x b3cmd-pgdump

PG_MAJOR=$(docker exec "%(container_name)s" env | grep PG_MAJOR | cut -d = -f 2)
PG_MAJOR=${PG_MAJOR:-9.4}
docker run --rm \
    --link "%(container_name)s:db" \
    --volume $(pwd):/b3cmd_util_pgdump \
    postgres:$PG_MAJOR \
    /b3cmd_util_pgdump/b3cmd-pgdump
''' % api.env)

    api.get(remote_path='%(workdir)s/%(container_name)s.dump' % api.env, local_path='%(container_name)s.dump' % api.env)
    api.run('rm -r %(workdir)s' % api.env)
