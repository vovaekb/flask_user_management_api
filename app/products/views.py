import os
from flask import render_template, Blueprint, request, jsonify, Response
from flask_cors import cross_origin
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
from app import app, CustomError
from app.models import Products
from app.serializers import ProductsSchema
from app.products.services import ProductService

# CONFIG
products_blueprint = Blueprint('products', __name__) # , template_folder='templates')
product_schema = ProductsSchema()
products_schema = ProductsSchema(many=True)


@products_blueprint.errorhandler(CustomError)
def handle_error(e):
    details = e.args[0]
    return Response(details['message'], status=200, mimetype='text/plain')

# ROUTES
@products_blueprint.route('/products/images-list', methods=['GET'])
@cross_origin()
def images_list():
    payload = ProductService.get_images()
    return jsonify(payload)


@products_blueprint.route('/products', methods=['GET', 'POST'])
@cross_origin()
def index():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        product = ProductService.create_product(data)
        return jsonify(product)
    else:
        payload = ProductService.get_products()
        return jsonify(payload)


@products_blueprint.route('/products/<product_id>', methods=['GET', 'PUT', 'DELETE'])
@cross_origin()
def product(product_id):
    if request.method == 'PUT':
        data = request.get_json()
        ProductService.update_product(product_id, data)
        text = 'OK'
        return Response(text, status=200)
    elif request.method == 'DELETE':
        ProductService.delete_product(product_id)
        text = 'OK'
        return Response(text, status=200)
    elif request.method == 'GET':
        product = ProductService.get_product(product_id)
        return jsonify(product)
