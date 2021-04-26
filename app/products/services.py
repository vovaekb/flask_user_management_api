import os
from sqlalchemy.sql import func
from app import app, APP_ROOT
from app.models import Products
from app.serializers import ProductsSchema

product_schema = ProductsSchema()
products_schema = ProductsSchema(many=True)

class ProductService:
    def get_images():
        # print('ProductService.get_images()')
        images_dir = 'public/assets/products/'
        image_files = [f for f in os.listdir(os.path.join(APP_ROOT, images_dir)) if not f.startswith('.')]
        image_files = list(map(lambda f: "%s/assets/products/%s" % (app.config['REMOTE'], f), image_files))
        return image_files

    def get_products():
        # print('ProductService.get_products()')
        products = app.session.query(Products)
        products = products.order_by(Products.id.asc()).all()
        products_dict = products_schema.dump(products)
        print(products_dict)
        return products_dict

    def get_product(product_id):
        print('ProductService.get_product()')
        print(product_id)
        product = app.session.query(Products).filter_by(id=product_id).first()
        print(product.title)
        data = product_schema.dump(product)
        print(data)
        return data

    def update_product(product_id, data):
        # print('ProductService.update_product')
        product = app.session.query(Products).filter_by(id=product_id).first()
        # print(product)
        product.title = data.get('title', None)
        product.subtitle = data.get('subtitle', None)
        product.img = data.get('img', None)
        product.price = data.get('price', None)
        product.rating = data.get('rating', None)
        product.code = data.get('code', None)
        product.hashtag = data.get('hashtag', None)
        product.technology = data.get('technology', None)
        product.discount = data.get('discount', None)
        product.description_1 = data.get('description_1', None)
        product.description_2 = data.get('description_2', None)
        product.updatedAt = func.now()
        app.session.add(product)
        app.session.commit()


    def create_product(data):
        # print('ProductService.create_product')
        product = Products(
            title = data.get('title', None),
            subtitle = data.get('subtitle', None),
            img = data.get('img', None),
            price = data.get('price', None),
            rating = data.get('rating', None),
            code = data.get('code', None),
            hashtag = data.get('hashtag', None),
            technology = data.get('technology', None),
            discount = data.get('discount', None),
            description_1 = data.get('description_1', None),
            description_2 = data.get('description_2', None),
            updatedAt=func.now()
        )
        app.session.add(product)
        app.session.commit()
        product = product_schema.dump(product)
        return product

    def delete_product(product_id):
        # print('ProductService.delete_product')
        product = app.session.query(Products).filter_by(id=product_id).first()
        print(product)
        app.session.delete(product)
        app.session.commit()
