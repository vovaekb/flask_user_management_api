import os
from flask import render_template, abort, Blueprint, request, Response, jsonify, send_file, send_from_directory
from flask_cors import cross_origin
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
from app import app, ALLOWED_EXTENSIONS, FILE_FOLDER, APP_ROOT, get_current_user, ForbiddenError
# from app.models import ...
from app.models import Users, Files
from app.serializers import UsersSchema, FilesSchema
from app.files.services import FileService

# CONFIG
files_blueprint = Blueprint('files', __name__) #, template_folder='templates')
file_schema = FilesSchema()
files_schema = FilesSchema(many=True)
user_schema = UsersSchema()
users_schema = UsersSchema(many=True)


@files_blueprint.errorhandler(ForbiddenError)
def handle_forbidden_error(e):
    details = e.args[0]
    return Response(details['message'], status=403, mimetype='text/plain')

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(403)
def forbidden(e):
    return jsonify(error=str(e)), 403

@app.errorhandler(500)
def internal_server_error(e):
    #print('error handler')
    #print(e)
    return jsonify(error=str(e)), 500


# ROUTES
@files_blueprint.route('/file/download', methods=['GET'])
@cross_origin(supports_credentials=True)
def download():
    privateUrl = request.args['privateUrl']
    #print(privateUrl)

    if privateUrl is None:
        abort(404, description='Not found')
    # return file to download
    file_path = os.path.join(APP_ROOT, 'static', privateUrl)
    print(file_path)
    return send_file(file_path, as_attachment=True) # "%s/%s" % (APP_ROOT, privateUrl)) # FILE_FOLDER


@files_blueprint.route('/file/upload/users/avatar', methods=['POST'])
@cross_origin(supports_credentials=True)
@get_current_user
def upload_users_avatar(current_user):
    if not current_user:
        raise ForbiddenError({'message': 'Upload user avatar error: Forbidden\n'})
    folder = 'static/users/avatar'
    validations = {}
    FileService.file_request(folder, request, validations)

    return Response('OK', status=200)
