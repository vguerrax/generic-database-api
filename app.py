# -*- coding: UTF-8 -*-
import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from db import executa_query

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

tipos_servidores = ('MySQL')
json = \
{
	"conexao" : 
	{
		"type" : "Tipo de servidor de banco de dados, um dos tipos [" + str(tipos_servidores) + "]",
		"host" : "Nome ou IP do servidor de banco de dados",
		"database" : "Nome do banco de dados",
		"user" : "Usuário para conexão",
		"password" : "Senha para conexão"
	},
	"query" : "Comando SQL para execução"
}

@app.route("/")
@cross_origin()
def hello():
    return jsonify({'msg': "Olá mundo!!"})

@app.route("/run", methods=['GET', 'PUT'])
@cross_origin()
def run():
    response = None
    if request.method == 'GET':
        response = jsonify(json)
        return response
    elif request.method == 'PUT':
        dados_conexao = request.get_json()['conexao']
        query = request.get_json()['query']
        retorno = executa_query(dados_conexao, query)
        response = jsonify(retorno)
        return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)