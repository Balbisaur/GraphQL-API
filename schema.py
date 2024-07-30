import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import Product as ProductModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Creating an engine and session
engine = create_engine('sqlite:///bakery.db')
Session = sessionmaker(bind=engine)
session = Session()

# Defining GraphQL Product Type
class ProductType(SQLAlchemyObjectType):
    class Meta:
        model = ProductModel

# Defining the Queries
class Query(graphene.ObjectType):
    products = graphene.List(ProductType)
    search_products = graphene.List(ProductType, name=graphene.String(), category=graphene.String())

    def resolve_products(self, info):
        return session.query(ProductModel).all()

    def resolve_search_products(self, info, name=None, category=None):
        query = session.query(ProductModel)
        if name:
            query = query.filter(ProductModel.name.ilike(f'%{name}%'))
        if category:
            query = query.filter(ProductModel.category.ilike(f'%{category}%'))
        return query.all()

# Defining Mutations
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        quantity = graphene.Int(required=True)
        category = graphene.String(required=True)
    
    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, quantity, category):
        new_product = ProductModel(name=name, price=price, quantity=quantity, category=category)
        session.add(new_product)
        session.commit()
        return CreateProduct(product=new_product)

class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        price = graphene.Float()
        quantity = graphene.Int()
        category = graphene.String()
    
    product = graphene.Field(ProductType)

    def mutate(self, info, id, name=None, price=None, quantity=None, category=None):
        product = session.query(ProductModel).filter_by(id=id).first()
        if not product:
            return UpdateProduct(product=None)
        if name:
            product.name = name
        if price:
            product.price = price
        if quantity:
            product.quantity = quantity
        if category:
            product.category = category
        session.commit()
        return UpdateProduct(product=product)

class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    success = graphene.Boolean()

    def mutate(self, info, id):
        product = session.query(ProductModel).filter_by(id=id).first()
        if not product:
            return DeleteProduct(success=False)
        session.delete(product)
        session.commit()
        return DeleteProduct(success=True)

class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

