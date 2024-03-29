import os
from flask import Blueprint, request, jsonify, Response, send_file
from sqlalchemy.exc import SQLAlchemyError

from app import app, CustomError, APP_ROOT
from app.products.services import ProductService
from app.serializers import ProductsSchema

products_blueprint = Blueprint('products', __name__)
product_schema = ProductsSchema()
products_schema = ProductsSchema(many=True)


@products_blueprint.errorhandler(SQLAlchemyError)
def handle_exception(e):
    details = e.args[0]
    return Response(details, status=555, mimetype='text/plain')


@products_blueprint.errorhandler(CustomError)
def handle_error(e):
    details = e.args[0]
    return Response(details['message'], status=500, mimetype='text/plain')


# ROUTES
@products_blueprint.route('/products/images-list', methods=['GET'])
def images_list():
    payload = ProductService.get_images()
    return jsonify(payload)


@products_blueprint.route('/products', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            data = request.get_json()
            product = ProductService.create_product(data)
            return jsonify(product)
        except SQLAlchemyError as e:
            print("Unable to add product to database.")
            app.session.rollback()
            details = e.args[0]
            return Response(details, status=555, mimetype='text/plain')
    else:
        try:
            payload = ProductService.get_products()
            return jsonify(payload)
        except SQLAlchemyError as e:
            print("Unable to get products in database.")
            details = e.args[0]
            return Response(details, status=555, mimetype='text/plain')


@products_blueprint.route('/products/<product_id>', methods=['GET', 'PUT', 'DELETE'])
def product(product_id):
    if request.method == 'PUT':
        try:
            data = request.get_json()
            ProductService.update_product(product_id, data)
            text = 'OK'
            return Response(text, status=200)
        except SQLAlchemyError as e:
            print("Unable to update product in database.")
            app.session.rollback()
            details = e.args[0]
            return Response(details, status=555, mimetype='text/plain')

    elif request.method == 'DELETE':
        try:
            ProductService.delete_product(product_id)
            text = 'OK'
            return Response(text, status=200)
        except SQLAlchemyError as e:
            print("Unable to get product from database.")
            app.session.rollback()
            details = e.args[0]
            return Response(details, status=555, mimetype='text/plain')
    elif request.method == 'GET':
        try:
            product = ProductService.get_product(product_id)
            return jsonify(product)
        except SQLAlchemyError as e:
            print("Unable to get product from database.")
            details = e.args[0]
            return Response(details, status=555, mimetype='text/plain')


@products_blueprint.route('/assets/products/<path:filename>', methods=['GET'])
def product_image(filename):
    file_path = os.path.join(APP_ROOT, 'static/assets/products/', filename)
    return send_file(file_path, as_attachment=True)
