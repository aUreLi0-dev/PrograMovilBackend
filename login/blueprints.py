from login.views import view as main_views
from login.apis import api as main_apis
from notas.blueprints import blueprints as notas_blueprints

def register(app):
  modules_blueprints = [
    notas_blueprints,
  ]
  app.register_blueprint(main_views)
  app.register_blueprint(main_apis)
  for blueprints in modules_blueprints:
    for blueprint in blueprints:
      app.register_blueprint(blueprint)

