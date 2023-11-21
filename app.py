from flask import Flask
from game1.game1 import game1
from game2.game2 import game2
from game3.game3 import game3
from game4.game4 import game4
from macro1.macro1 import macro1
from macro2.macro2 import macro2
from macro3.macro3 import macro3
from mining.mining import mining
from main.main import main
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "virtualecon.json"

app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)

app.register_blueprint(main)
app.register_blueprint(game1, url_prefix='/game1')
app.register_blueprint(game2, url_prefix='/game2')
app.register_blueprint(game3, url_prefix='/game3')
app.register_blueprint(game4, url_prefix='/game4')
app.register_blueprint(macro1, url_prefix='/macro1')
app.register_blueprint(macro2, url_prefix='/macro2')
app.register_blueprint(macro3, url_prefix='/macro3')
app.register_blueprint(mining, url_prefix='/mining')


app.config['SECRET_KEY'] = 'thisisasecret'
app.config['SESSION_PERMANENT'] = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
