from logging import StreamHandler
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from flask import Flask, request, jsonify, render_template
from . import extensions


class Application(object):
    app_name = __name__
    BLUEPRINTS = {}

    def __init__(self, root_folder, settings_module_override=None):
        sys.path.append(root_folder)
        self.root_folder = root_folder
        self.setting_module_override = settings_module_override

    @property
    def settings_env_name(self):
        app_env_name = self.app_name.replace('_', '').replace('-', '').upper()
        return '{}_SETTINGS_MODULE'.format(app_env_name)

    @property
    def default_settings_path(self):
        return '{}.settings.DevelopmentConfig'.format(self.app_name)

    @property
    def settings_path(self):
        env_var = os.environ.get(
            self.settings_env_name,
            self.setting_module_override or self.default_settings_path
        )
        return env_var

    def create_app(self):
        app = Flask(self.app_name)

        self.load_app_settings(app, self.settings_path)
        self.load_extensions(app)
        self.configure_logging(app)
        self.setup_errorhandlers(app)
        self.setup_views(app)

        return app

    def load_app_settings(self, app, settings_path):
        app.logger.info("Loading settings from {}".format(settings_path))
        app.config.from_object(settings_path)

    def load_extensions(self, app):
        extensions.db.init_app(app)
        extensions.migrate.init_app(app, extensions.db)

        if app.config['TOOLBAR_ENABLED']:
            extensions.toolbar.init_app(app)

    def setup_errorhandlers(self, app):
        if app.config['DEBUG']:
            return

        @app.errorhandler(404)
        def page_not_found(error):
            if request.is_xhr:
                return jsonify(error='Sorry, page not found')
            return render_template("errors/404.html", error=error), 404

        @app.errorhandler(403)
        def forbidden(error):
            if request.is_xhr:
                return jsonify(error='Sorry, not allowed')
            return render_template("errors/403.html", error=error), 403

        @app.errorhandler(500)
        def server_error(error):
            if request.is_xhr:
                return jsonify(error='Sorry, an error has occurred')
            return render_template("errors/500.html", error=error), 500

    def configure_logging(self, app):

        """
        if not app.config['DEBUG']:
            mail_handler = \
                SMTPHandler(app.config['MAIL_SERVER'],
                            app.config['MAIL_FROM_EMAIL'],
                            app.config['ADMINS'],
                            'application error',
                            (
                                app.config['MAIL_USERNAME'],
                                app.config['MAIL_PASSWORD'],
                            ))

            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        """

        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]')

        stream_handler = StreamHandler()
        app.logger.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)

        debug_log = app.config.get('DEBUG_LOG')
        error_log = app.config.get('ERROR_LOG')

        if debug_log:
            debug_file_handler = \
                RotatingFileHandler(debug_log,
                                    maxBytes=100000,
                                    backupCount=10)

            debug_file_handler.setLevel(logging.DEBUG)
            debug_file_handler.setFormatter(formatter)
            app.logger.addHandler(debug_file_handler)

        if error_log:
            error_file_handler = \
                RotatingFileHandler(error_log,
                                    maxBytes=100000,
                                    backupCount=10)

            error_file_handler.setLevel(logging.ERROR)
            error_file_handler.setFormatter(formatter)
            app.logger.addHandler(error_file_handler)

    def setup_views(self, app):
        for url_prefix, blueprint in self.BLUEPRINTS.items():
            app.register_blueprint(blueprint, url_prefix=url_prefix)
