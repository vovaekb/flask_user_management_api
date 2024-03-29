import os
import flask
from flask import Flask, _app_ctx_stack, request, Response
from flask_cors import CORS
from flask_mail import Mail
from whitenoise import WhiteNoise
import jwt
from functools import wraps, update_wrapper
from sqlalchemy.orm import scoped_session
from app.database import SessionLocal, engine, Base
from app.models import Users
from config import Config, DevConfig, ProductionConfig


# Create database structure
# Base.metadata.create_all(bind=engine)

FILE_FOLDER = 'static/'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
print(APP_ROOT)

app = Flask(__name__)
CORS(app, supports_credentials=True)
# add serving static files
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
app.session = scoped_session(SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)
app.secret_key = os.environ.get('FN_FLASK_SECRET_KEY', default=False)

# if os.environ['FLASK_DEV'] == True:
print('Dev env')
app.config.from_object(DevConfig)
'''
else:
    print('Prod env')
    app.config.from_object(ProductionConfig)
'''

# print(app.config['UPLOAD_FOLDER'])
# print(app.config['MAIL_SERVER'])
print(app.config['REMOTE'])

mail = Mail(app)

# Global methods and classes


# Error handlers
class CustomError(Exception):
    pass


# Error handlers
class ValidationError(Exception):
    pass


# Error handlers
class ForbiddenError(Exception):
    pass


def get_current_user(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        print('get_current_user')

        if 'Authorization' in request.headers and len(
            request.headers['Authorization'].split(' ')
        ) > 1:
            token = request.headers['Authorization'].split(' ')[1]
            print('token: ', token)

            try:
                data = jwt.decode(
                    token, app.config['SECRET_KEY'], 
                    algorithms='HS256'
                )
                user = data['user'] 
                print(data)
                print(user)
                current_user = app.session.query(Users) \
                    .filter(Users.id == user['id']) \
                    .filter(Users.email == user['email']).first()
                print(current_user)
            except Exception as e:
                print('Error when decoding token: ', str(e))
                raise CustomError({'message': 'Error when verifying token: token is invalid\n'})
        else:
            current_user = None

        return f(current_user, *args, **kwargs)
    return decorator


def no_cache(view):
    @wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache_impl, view)


def token_included(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        print('token_included')
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
            print('token: ', token)

        if not token:
            current_user = None

@app.after_request
def set_headers(response):
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response


# BLUEPRINTS
from app.auth.views import auth_blueprint
from app.files.views import files_blueprint
from app.users.views import users_blueprint
from app.products.views import products_blueprint
from app.analytics.views import analytics_blueprint

app.register_blueprint(auth_blueprint, url_prefix='/api')
app.register_blueprint(files_blueprint, url_prefix='/api')
app.register_blueprint(users_blueprint, url_prefix='/api')
app.register_blueprint(products_blueprint, url_prefix='/api')
app.register_blueprint(analytics_blueprint, url_prefix='/api')

# from app import views
