import os
import psycopg2
from flask import Flask, Blueprint, jsonify
from instance.config import app_config
from app.api.v2.views.user_views import v2_blue
from app.api.v2.views.meet_views import v_blue
from app.api.v2.models.db_connect import connect_db, db_init, create_admin


def create_app(name_conf):
    my_app = Flask(__name__, instance_relative_config=True)
    my_app.config.from_object(app_config[name_conf])
    my_app.config.from_pyfile('config.py')

    try:
        conn = connect_db()
        db_init(conn)
        create_admin(conn)

    except Exception as error:
        print('Error creating tables: {}'.format(str(error)))

    my_app.register_blueprint(v2_blue, url_prefix="/api/v2/auth")
    my_app.register_blueprint(v_blue, url_prefix="/api/v2")

    @my_app.errorhandler(404)
    def page_not_found(error):
        return jsonify({'error': 'Url not found', 'status': 404}), 404

    @my_app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed', 'status': 405}), 40

    @my_app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad Request', 'status': 400}), 400

    return my_app
