import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader('template'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
)
template = env.get_template('index.html')
src_dir = os.path.dirname(os.path.abspath(__file__))

dest_dir = os.path.join(src_dir, '../docs/')
dest_dir = os.path.dirname(os.path.abspath(dest_dir))
print(dest_dir)
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

f = open('../docs/index.html', 'w')
f.write(template.render())
f.close()
