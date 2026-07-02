from main.views import view as main_views
from main.apis import api as main_apis
from notas.blueprints import blueprints as notas_blueprints
from descripcion_cursos.blueprints import blueprints as descripcion_cursos_blueprints

def register(app):
  modules_blueprints = [
    notas_blueprints,
    descripcion_cursos_blueprints,
  ]
  app.register_blueprint(main_views)
  app.register_blueprint(main_apis)
  for blueprints in modules_blueprints:
    for blueprint in blueprints:
      app.register_blueprint(blueprint)

