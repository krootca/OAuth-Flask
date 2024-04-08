from flask import Flask, render_template
from decouple import config
 
# Public links
from app.routes.public import public_blueprint

#
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

#config
app.config['SECRET_KEY'] = config('SECRET_KEY')





### imports routes public
app.register_blueprint(public_blueprint)