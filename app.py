# !/usr/bin/env python
# -*- coding: utf-8 -*-
from apps.login.application import APP
from apps.login.blueprints import register
from apps.login.middlewares import not_found

if __name__ == '__main__':
  register(APP)
  APP.register_error_handler(404, not_found)
  # run app
  APP.run(
    debug=True,
    host='0.0.0.0',
    port=5000
  )
