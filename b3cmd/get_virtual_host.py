from fabric import api


def get_virtual_host(default):
    virtual_host_simple = None
    virtual_host_custom = None

    try:
        if api.env.virtual_host_simple:
            virtual_host_simple = api.env.project_name
    except BaseException:
        pass

    try:
        virtual_host_custom = api.env.virtual_host_custom
    except BaseException:
        pass

    return prepend_namespace(
        virtual_host_custom or virtual_host_simple or default
    )


def prepend_namespace(host):
    if api.env.namespace != api.env.namespace_from_server:
        return ('%(namespace)s--' % api.env) + host

    return host
