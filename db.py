# -*- coding: UTF-8 -*-
import sys
import pymysql

def obtem_conexao(dados_conexao):
    if dados_conexao['type'] == 'MySQL':
        return obtem_conexao_mysql(dados_conexao)

def obtem_conexao_mysql(dados_conexao):
    conexao = pymysql.connect(host=dados_conexao['host'],
                             user=dados_conexao['user'],
                             password=dados_conexao['password'],
                             db=dados_conexao['database'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    return conexao

def executa_query(dados_conexao, query):
    conexao = obtem_conexao(dados_conexao)
    retorno = {}
    linhas_afetadas = 0
    try:
        with conexao.cursor() as cursor:
            linhas_afetadas = cursor.execute(query)
            retorno["linhas_afetadas"] = linhas_afetadas
            #if 'SELECT' in str(query).upper() or 'SHOW' in str(query).upper():
            linhas = cursor.fetchall()
            retorno["dados"] =  linhas
        conexao.commit()
    except:
        err = sys.exc_info()[1]
        retorno["mensagem"] = "Erro ao executar a query [" + query + "]"
        retorno["erro"] = str(err)
        conexao.rollback()
    finally:
        conexao.close()
    return retorno