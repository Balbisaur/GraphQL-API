from flask import Flask, request, jsonify
from flask_graphql import GraphQLView
from schema import schema

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the Bakery GraphQL API!"

# Adding GraphQL endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Enabling the GraphiQL interface
    )
)

if __name__ == '__main__':
    app.run(debug=True)


#http://127.0.0.1:5000/graphql enter into your browser

