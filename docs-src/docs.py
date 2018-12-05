from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader('template'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
)

template = env.get_template('index.html')

f = open('index.html', 'w')
f.write(template.render())
f.close()
