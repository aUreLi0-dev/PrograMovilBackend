from apps.login.views import view as main_views
from apps.login.apis import api as main_apis
from apps.notas.blueprints import blueprints as notas_blueprints
from apps.descripcion_cursos.blueprints import blueprints as descripcion_cursos_blueprints
from apps.malla.blueprints import blueprints as malla_blueprints
from apps.especialidades.blueprints import blueprints as especialidades_blueprints
from apps.horario.blueprints import blueprints as horario_blueprints

def register(app):
  modules_blueprints = [
    notas_blueprints,
    descripcion_cursos_blueprints,
    malla_blueprints,
    especialidades_blueprints,
    horario_blueprints,
  ]
  app.register_blueprint(main_views)
  app.register_blueprint(main_apis)
  for blueprints in modules_blueprints:
    for blueprint in blueprints:
      app.register_blueprint(blueprint)

