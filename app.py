from flask import Flask
from game1.game1 import game1
from game2.game2 import game2
from game3.game3 import game3
from game4.game4 import game4
from main.main import main

app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)

app.register_blueprint(main)
app.register_blueprint(game1, url_prefix='/game1')
app.register_blueprint(game2, url_prefix='/game2')
app.register_blueprint(game3, url_prefix='/game3')
app.register_blueprint(game4, url_prefix='/game4')

app.config['SECRET_KEY'] = 'thisisasecret'
app.config['SESSION_PERMANENT'] = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
