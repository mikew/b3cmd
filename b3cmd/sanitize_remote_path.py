import re
import os


finder = re.compile(r'^(\s*(\.*\/*)*)')
ERROR_MESSAGE_OOB = 'sanitize_remote_path: `%s` is outside its directory'
safe_paths = (
    '.',
    './',
    './*',
    './**/*',
)


def sanitize_remote_path(remote_path):
    if remote_path in safe_paths:
        return remote_path

    fakepath = '/tmp/project'
    sanitized = finder.sub('', remote_path)
    no_splat = sanitized.replace('*', '')

    if not is_subdir(os.path.join(fakepath, no_splat), fakepath):
        raise Exception(ERROR_MESSAGE_OOB % remote_path)

    return sanitized


def is_subdir(path, directory):
    path = os.path.realpath(path)
    directory = os.path.realpath(directory)
    return path.startswith(directory)
