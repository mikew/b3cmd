from fabric.tasks import execute
from fabric.network import disconnect_all


def fabric_execute(fn, *args, **kwargs):
    try:
        execute(fn, *args, **kwargs)
    finally:
        disconnect_all()
