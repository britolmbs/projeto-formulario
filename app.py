from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from io import BytesIO
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'  
app.config['SECRET_KEY'] = 'chave_secreta'  
db = SQLAlchemy(app)

# Definição do Modelo
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)  
    email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Cliente {self.nome}>'


@app.route('/')
def index():
    return redirect(url_for('adicionar_cliente'))


@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        email = request.form['email']

        novo_cliente = Cliente(nome=nome, endereco=endereco, telefone=telefone, email=email)
        try:
            db.session.add(novo_cliente)
            db.session.commit()
            flash('Cliente adicionado com sucesso!', 'success')
            return redirect(url_for('consultar_cliente'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar cliente: {e}', 'danger')
    return render_template('formulario.html')


@app.route('/consultar', methods=['GET', 'POST'])
def consultar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        clientes = Cliente.query.filter(Cliente.nome.ilike(f'%{nome}%')).all()  

        if clientes:
            return render_template('procurar.html', clientes=clientes, nome=nome)
        else:
            flash(f'Nenhum cliente encontrado com o nome "{nome}".', 'warning')
            return redirect(url_for('consultar_cliente'))
    return render_template('clientes.html')


@app.route('/exportar', methods=['POST'])
def exportar_clientes():
    nome = request.form['nome']
    clientes = Cliente.query.filter(Cliente.nome.ilike(f'%{nome}%')).all()

    if not clientes:
        flash('Nenhum cliente para exportar.', 'warning')
        return redirect(url_for('consultar_cliente'))

    dados = {
        'Nome': [cliente.nome for cliente in clientes],
        'Endereço': [cliente.endereco for cliente in clientes],
        'Telefone': [cliente.telefone for cliente in clientes],
        'Email' : [cliente.email for cliente in clientes],
    }
    df = pd.DataFrame(dados)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Clientes')
    output.seek(0)

    return send_file(
        output,
        download_name="clientes.xlsx",  
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Banco de dados criado com sucesso!")
    app.run(debug=True)
