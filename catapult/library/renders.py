import os
from jinja2 import Environment, BaseLoader, FileSystemLoader


def render_path(path, context):
    path, filename = os.path.split(path)

    return Environment(
        loader=FileSystemLoader(path)
    ).get_template(filename).render(context)


def render_string(string, context):
    template = Environment(loader=BaseLoader).from_string(string)

    return template.render(context)


def render_shared(template_path, dest, storage, paths, host):
    storage.start_host(host)
    generated = render_path(template_path, {
        'storage': storage.get,
        'paths': paths.get,
    })
    storage.finish_host()

    with open(dest, 'w') as open_file:
        open_file.write(generated)
