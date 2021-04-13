import os
from flask import render_template, abort, Blueprint, request, Response, jsonify, send_file, send_from_directory
from flask_cors import cross_origin
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
from app import app, ALLOWED_EXTENSIONS, FILE_FOLDER, APP_ROOT
# from app.models import ...
from app.models import Users, Files
from app.serializers import UsersSchema, FilesSchema


# CONFIG
files_blueprint = Blueprint('files', __name__) #, template_folder='templates')
file_schema = FilesSchema()
files_schema = FilesSchema(many=True)
user_schema = UsersSchema()
users_schema = UsersSchema(many=True)


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ROUTES
@files_blueprint.route('/files/download', methods=['GET'])
@cross_origin()
def download():
    privateUrl = request.args['privateUrl']
    print(privateUrl)
    path = os.path.join(app.config['UPLOAD_FOLDER'], privateUrl) #  folder, filename)

    if privateUrl is None:
        abort(404, description='Not found')
    # return file to download

    file_path = os.path.join(APP_ROOT, 'static', privateUrl)
    print(file_path)
    return send_file(file_path, as_attachment=True) # "%s/%s" % (APP_ROOT, privateUrl)) # FILE_FOLDER
    # return send_file("%s/%s" % (app.config['UPLOAD_FOLDER'], privateUrl))
    # return send_from_directory(app.config['UPLOAD_FOLDER'], privateUrl)


@files_blueprint.route('/files/upload/users/avatar', methods=['POST'])
@cross_origin()
def upload_users_avatar():
    folder = 'static/users/avatar'
    
    if not 'file' in request.files:
        abort(500)
    
    file = request.files['file']
    print(request.files['file'])
    
    if file and allowed_file(file.filename):
        filename = file.filename # secure_filename(file.filename)
        # privateUrl = os.path.join(app.config['UPLOAD_FOLDER'], folder, filename)
        privateUrl = os.path.join(APP_ROOT, folder, filename)
        print(privateUrl)
        file.save(privateUrl)
    return Response('OK', status=200)
