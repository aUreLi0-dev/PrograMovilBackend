from main.application import APP
from main.blueprints import register
from main.middlewares import not_found


if __name__ == '__main__':
    register(APP)
    APP.register_error_handler(404, not_found)
    APP.run(
        debug=False,
        host='0.0.0.0',
        port=5000,
        use_reloader=False,
    )
