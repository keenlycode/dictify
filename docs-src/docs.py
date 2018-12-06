from sanic import Sanic, response
from jinja2 import Environment, FileSystemLoader, select_autoescape
import mistune

app = Sanic()
app.static('/static', '../docs/static/')
jinja = Environment(
    loader=FileSystemLoader('template'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
)
markdown = mistune.Markdown(escape=False)

@app.route('/')
async def home(request):
    template = jinja.get_template('index.html')
    body = open('template/index/body.md')
    body = markdown(body.read())
    return response.html(template.render(body=body))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
