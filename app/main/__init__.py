from flask import Blueprint

'''
app.route decorator exists only after create_app() is invoked.
To define routes/error handlers. Remain in dormant state until blueprint \
 is registered with an app.
'''

main = Blueprint('main', __name__)

# To import modules at bottom to avoid circular dependency
# Both views/errors are in turn going to import the main blueprint object

from app.main.endpoints import auth
