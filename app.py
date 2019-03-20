# -*- coding: UTF-8 -*-
import os
from flask import Flask, request, jsonify
from db import executa_query

app = Flask(__name__)

tipos_servidores = ('MySQL')
json = \
{
	"conexao" : 
	{
		"type" : "Tipo de servidor de banco de dados, um dos " + str(tipos_servidores),
		"host" : "Nome ou IP do servidor de banco de dados",
		"database" : "Nome do banco de dados",
		"user" : "Usuário para conexão",
		"password" : "Senha para conexão"
	},
	"query" : "Comando SQL para execução"
}

@app.route("/")
def hello():
    return "Olá mundo!!"

@app.route("/run", methods=['GET', 'PUT'])
def run():
    response = None
    if request.method == 'PUT':
        response = jsonify(json)
        return response
    elif request.method == 'POST':
        dados_conexao = request.get_json()['conexao']
        query = request.get_json()['query']
        retorno = executa_query(dados_conexao, query)
        response = jsonify(retorno)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)