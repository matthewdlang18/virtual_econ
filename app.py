from flask import Flask
from game1.game1 import game1
from game2.game2 import game2
from main.main import main

app = Flask(__name__)

app.register_blueprint(main)
app.register_blueprint(game1, url_prefix='/game1')
app.register_blueprint(game2, url_prefix='/game2')

app.config['SECRET_KEY'] = 'thisisasecret'
app.config['SESSION_PERMANENT'] = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
