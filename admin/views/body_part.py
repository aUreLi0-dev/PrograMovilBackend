from flask import Blueprint, render_template, request, redirect
from main.database import Session
from main.models import BodyPart

view = Blueprint('admin_body_part_views', __name__, template_folder='../templates')

@view.route('/admin/body-parts', methods=['GET'])
def home():
  # accaeso a datos
  session = Session()
  body_parts = session.query(BodyPart).all() # SELECT * FROM body_parts;
  # render
  locals = {
    'title': 'Nosotros',
    'nav': 'nosotros',
    'body_parts': body_parts,
  }
  #return render_template('body_part/index.html', locals=locals)
  return render_template('admin.html', locals=locals)

@view.route('/admin/body-parts/add', methods=['GET'])
def agregar():
  # render
  locals = {
    'title': 'Nosotros',
    'nav': 'nosotros',
  }
  return render_template('body_part/agregar.html', locals=locals)

@view.route('/admin/body-parts/create', methods=['POST'])
def create_body_part():
  # data
  name = request.form.get('name')
  # blogic
  session = Session()
  body_part = BodyPart(
    name=name
  )
  # Agregar y confirmar la inserción en la base de datos
  session.add(body_part)
  session.commit()
  return redirect('/admin/body-parts')

@view.route('/admin/body-parts/delete/<int:body_part_id>', methods=['GET'])
def delete_body_part(body_part_id):
  # blogic
  session = Session()
  body_part = session.query(BodyPart).filter_by(id=body_part_id).first()
  session.delete(body_part)
  session.commit()
  return redirect('/admin/body-parts')

@view.route('/admin/body-parts/edit/<int:body_part_id>', methods=['GET'])
def edit_body_part(body_part_id):
  # blogic
  session = Session()
  body_part = session.query(BodyPart).filter_by(id=body_part_id).first()
  locals = {
    'title': 'Nosotros',
    'nav': 'nosotros',
    'body_part': body_part
  }
  return render_template('body_part/editar.html', locals=locals)

@view.route('/admin/body-parts/update', methods=['POST'])
def update_body_part():
  # data
  id = request.form.get('id')
  name = request.form.get('name')
  # blogic
  session = Session()
  body_part = session.query(BodyPart).filter_by(id=id).first()
  if body_part:
    # Actualizar campos específicos
    body_part.name = name
    # Guardar los cambios
    session.commit()
    # Mostrar el registro actualizado
    return redirect('/admin/body-parts')
  else:
    return redirect('/admin/body-parts')
