# -*- coding: UTF-8 -*-
import os
from ast import literal_eval
from base64 import encodebytes
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from db import executa_query
from salt import salt_generator, key_salt_generator, decode_data
from datetime import datetime

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

salt_list = {}
dados_conexao = None
instrucoes = \
    "<h1>Generic Database API - API para conexão à banco de dados</h1>" + \
    "<p>Para utilizar siga os seguintes passos:" + \
    "<ol>" + \
    "<li>Faça uma requisição GET no caminho /salt</li>" + \
    "<li>Guarde o valor do header 'Key-Salt'</li>" + \
    "<li>Guarde o JSON da resposta *</li>" + \
    '<li>Crie uma string de conexão **</li>' + \
    "<li>Concatene a string de conexão com o valor do atributo 'value' do JSON obtido anteriormente</li>" + \
    "<li>Transforme a string de conexão concatenada para base64</li>" + \
    '<li>Faça uma requisição PUT no caminho /run passando no corpo da requisição a query para execução ({"query" : ""})</li>' + \
    "<li>Passe a string de conexão na base64 no header 'Data-Connectio'</li>" + \
    "<li>Passe o retorno do header 'Key-Salt' salvo anteriormente em um header de mesmo nome</li>" + \
    "</ol>" + \
    '<span> * { \
        "validate": "1553544271.63169", \
        "value": "1FSAG0DKPSD9DGYGG9Q3Z" \
        } \
    </span><br>' + \
    '<span> ** { "database" : "", "host": "", "password": "", "type": "MySQL", "user": "" }</span>' + \
    "</p>"

def get_salt(key):
    if key == None:
        return None
    gsalt = salt_list.get(key)
    if gsalt == None:
        return None
    if float(gsalt['validate']) < datetime.now().timestamp():
        salt_list.pop(key)
        return None
    else:
        return gsalt

def salve_salt_on_list(salt, host):
    now = datetime.now()
    key = key_salt_generator(host, now)
    salt_list[key] = salt
    return key

def validate_salt(salt):
    if salt == None:
        response = {'erro' : 'Salt inválido ou expirado', \
                    'mensagem' : 'O salt obtido com o Key-Salt informado não existe ou é inválido. \
                    Por favor gere outro Salt realizando um GET em \'/salt\''}
        return response
    else:
        return True

def validate_data_connection(dados_conexao, salt_value):
    if dados_conexao == None:
        response = {'erro' : 'Aussência dos dados de conexão', \
                    'mensagem' : 'Não foi possível identificar os dados de conexão. \
                    Por favor, informe os dados através do Header \'Data-Connection\'.'}
        return response
    dados_conexao = decode_data(dados_conexao, salt_value)
    try:
        dados_conexao = literal_eval(dados_conexao)
    except:
        response = {'erro' : 'Formatação inválida dos dados de conexão', \
                    'mensagem' : 'Não foi possível ler o JSON com os dados de conexão, \
                    a formatação parece estar incorreta.'}
        return response
    return (True, dados_conexao)

@app.route("/salt", methods=['GET', 'PUT'])
@cross_origin()
def gsalt():
    if request.method == 'GET':
        gsalt = salt_generator()       
        response = jsonify(gsalt)
        host = request.headers['Host']
        response.headers['Key-Salt'] = salve_salt_on_list(gsalt, host)
        return response
    elif request.method == 'PUT':
        key = request.get_json().get('key-salt')
        return jsonify(get_salt(key))

@app.route("/")
@cross_origin()
def hello():
    return instrucoes

@app.route("/test", methods=['GET', 'PUT'])
@cross_origin()
def test():
    response = None
    key = request.headers.get('Key-Salt')
    gsalt = get_salt(key)
    if request.method == 'GET':
        response = jsonify(gsalt)
        return response
    elif request.method == 'PUT':
        if gsalt == None:
            response = jsonify({'erro' : 'Salt inválido ou expirado', \
                'mensagem' : 'O salt obtido com o Key-Salt informado não existe ou é inválido. Por favor gere outro Salt realizando um GET em \'/salt\''})
            return response
        dados_conexao = request.headers.get('Data-Connection')
        if dados_conexao == None:
            response = jsonify({'erro' : 'Aussência dos dados de conexão', \
                'mensagem' : 'Não foi possível identificar os dados de conexão. Por favor, informe os dados através do Header \'Data-Connection\'.'})
            return response
        dados_conexao = decode_data(dados_conexao, gsalt['value'])
        print(dados_conexao)
        try:
            dados_conexao = literal_eval(dados_conexao)
        except Exception as err:
            response = jsonify({'erro' : 'Formatação inválida dos dados de conexão', \
                'mensagem' : 'Não foi possível ler o JSON com os dados de conexão, a formatação parece estar incorreta.', \
                'detalhes' : str(err)})
            return response
        # query = request.get_json()['query']
        # retorno = executa_query(dados_conexao, query)
        # response = jsonify(retorno)
        return jsonify(dados_conexao)

@app.route("/run", methods=['GET', 'PUT'])
@cross_origin()
def run():
    response = None
    if request.method == 'GET':
        return instrucoes
    elif request.method == 'PUT':
        key = request.headers.get('Key-Salt')
        salt = get_salt(key)
        salt_valid = validate_salt(salt)
        if salt_valid != True:
            return jsonify(salt_valid)
        dados_conexao = request.headers.get('Data-Connection')
        dados_conexao_valid = validate_data_connection(dados_conexao, salt.get('value'))
        if dados_conexao_valid[0] != True:
            return jsonify(dados_conexao_valid)
        query = request.get_json()['query']
        retorno = executa_query(dados_conexao_valid[1], query)
        response = jsonify(retorno)
        return response #jsonify(dados_conexao)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)