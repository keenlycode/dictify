from sanic import Sanic, response
from jinja2 import Environment, FileSystemLoader, select_autoescape
import mistune

jinja = Environment(
    loader=FileSystemLoader('template'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
)
markdown = mistune.Markdown(escape=False)

template = jinja.get_template('index.html')
body = open('template/index/body.md')
body = markdown(body.read())
f = open('../docs/index.html', 'w')
f.write(template.render(body=body))
f.close()
