#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, render_template

view = Blueprint('admin-view-user', __name__, template_folder='../templates')

@view.route('/admin/users', methods=['GET'])
def index():
  locals = {
    'title': 'Home',
    'nav_active': 'home',
    'message': '',
  }
  return render_template('user/index.html', locals=locals)

