#comm websocket/bot/criar salas etc
#api rest
from flask import Flask,request,jsonify
from flask_bcrypt import Bcrypt  # criptografia

api = Flask(__name__)
bcrypt = Bcrypt(api)

@api.route("/", methods=["GET"])
def raiz():
    return jsonify({"status": "ok", "mensagem": "API funcionando!"})

#rodar api
if __name__ == "__main__":
    api.run(host='0.0.0.0')