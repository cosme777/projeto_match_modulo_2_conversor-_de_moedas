from flask import Flask, render_template, request, make_response
import requests
import json
from babel.numbers import format_currency
from datetime import datetime
import pytz

app = Flask(__name__)

MOEDAS = ["Escolha a moeda","USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "BRL"]

@app.route('/')
def index():
    # Recupera o histórico de simulações do cookie (ou cria uma lista vazia)
    historico_simulacoes = json.loads(request.cookies.get('historico_simulacoes', '[]'))
    return render_template('index.html', moedas=MOEDAS, historico_simulacoes=historico_simulacoes)

@app.route('/converter', methods=['POST'])
def converter():
    try:
        valor_input = request.form['valor'].replace(',', '.')
        valor = float(valor_input)
    except ValueError:
        return render_template('index.html', moedas=MOEDAS, erro=True)

    moeda_entrada = request.form['moeda_entrada']
    moeda_origem = request.form['moeda_origem']

    if moeda_entrada == "Escolha a moeda" or moeda_origem == "Escolha a moeda":
         return render_template('index.html', moedas=MOEDAS, erro_moeda=True)

    url = f"https://api.exchangerate-api.com/v4/latest/{moeda_entrada}"
    response = requests.get(url)
    data = json.loads(response.text)
    taxa_conversao = data["rates"][moeda_origem]

    valor_convertido = valor * taxa_conversao
    valor_convertido = "{:.2f}".format(valor_convertido)

    fuso_horario_brasil = pytz.timezone('America/Sao_Paulo')
    data_hora_brasil = datetime.now(fuso_horario_brasil)
    data_atual = data_hora_brasil.strftime("%d/%m/%y - %H:%M")

    historico_simulacoes = json.loads(request.cookies.get('historico_simulacoes', '[]'))

    simulacao = {
        'moeda_entrada': moeda_entrada,
        'moeda_origem': moeda_origem,
        'taxa_conversao': taxa_conversao,
        'valor': valor,
        'valor_convertido': valor_convertido,
        'data_atual': data_atual
    }

    historico_simulacoes.append(simulacao)

    # Define o histórico no cookie
    response = make_response(render_template('index.html', moedas=MOEDAS, resultado=True, historico_simulacoes=historico_simulacoes))
    response.set_cookie('historico_simulacoes', json.dumps(historico_simulacoes))

    return response

@app.route('/limpar')
def limpar():
    # Limpa o histórico no cookie
    response = make_response(render_template('index.html', moedas=MOEDAS, historico_simulacoes=[]))
    response.set_cookie('historico_simulacoes', '[]')
    return response

if __name__ == '__main__':
    app.run(debug=True)


