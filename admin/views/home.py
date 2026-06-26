from flask import Blueprint, render_template, session
from main.middlewares import only_logged

view = Blueprint('admin_views', __name__, template_folder='../templates')

@view.route('/admin')
@only_logged
def home():
  print(session)
  locals = {
    'title': 'Nosotros',
    'nav': 'nosotros',
  }
  return render_template('admin.html', locals=locals)

@view.route('/admin/hola')
def hola():
  return '<h1>Bienvenido a la página de admin/hola</h1>'

@view.route('/admin/demo')
def demo():
  return '<h1>Bienvenido a la página de admin/demo</h1>'
