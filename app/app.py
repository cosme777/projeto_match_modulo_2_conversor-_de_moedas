from flask import Flask, render_template, request
import requests
import json
from babel.numbers import format_currency
from datetime import datetime
import pytz

app = Flask(__name__)

MOEDAS = ["Escolha a moeda","USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "BRL"]
historico_simulacoes = []

@app.route('/')
def index():
    return render_template('index.html', moedas=MOEDAS, historico_simulacoes=historico_simulacoes)

@app.route('/converter', methods=['POST'])
def converter():
    try:
        # Substituir vírgulas por pontos no valor de entrada
        valor_input = request.form['valor'].replace(',', '.')
        valor = float(valor_input)
    except ValueError:
        return render_template('index.html', moedas=MOEDAS, historico_simulacoes=historico_simulacoes, erro=True)


    moeda_entrada = request.form['moeda_entrada']
    moeda_origem = request.form['moeda_origem']

    ### Implementado - - Verifica se as moedas selecionadas são válidas
    if moeda_entrada == "Escolha a moeda" or moeda_origem == "Escolha a moeda":
         return render_template('index.html', moedas=MOEDAS, historico_simulacoes=historico_simulacoes, erro_moeda=True)

    # Obtém a taxa de conversão
    url = f"https://api.exchangerate-api.com/v4/latest/{moeda_entrada}"
    response = requests.get(url)
    data = json.loads(response.text)
    taxa_conversao = data["rates"][moeda_origem]

    # Realiza a conversão
    valor_convertido = valor * taxa_conversao

    # Formata o valor convertido
    valor_convertido = "{:.2f}".format(valor_convertido)

    # Obtém a data e hora atual no formato especificado
    fuso_horario_brasil = pytz.timezone('America/Sao_Paulo')
    data_hora_brasil = datetime.now(fuso_horario_brasil)
    data_atual = data_hora_brasil.strftime("%d/%m/%y - %H:%M")

    # Adiciona a simulação ao histórico
    simulacao = {
        'moeda_entrada': moeda_entrada,
        'moeda_origem': moeda_origem,
        'taxa_conversao': taxa_conversao,
        'valor': valor,
        'valor_convertido': valor_convertido,
        'data_atual': data_atual
    }
    historico_simulacoes.append(simulacao)

    # Renderiza a página com o resultado incorporado
    return render_template('index.html', moedas=MOEDAS, resultado=True, historico_simulacoes=historico_simulacoes)

@app.route('/limpar')
def limpar():
    global historico_simulacoes
    historico_simulacoes = []
    return render_template('index.html', moedas=MOEDAS, historico_simulacoes=historico_simulacoes)

if __name__ == '__main__':
    app.run(debug=True)
