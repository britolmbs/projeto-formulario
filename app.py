from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://banco.db'
app.config['SECRET_KEY'] = 'chave'
db = SQLAlchemy(app)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    telfone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Cliente {self.nome}>'
    
    @app.route('/')
    def index():
        return redirect(url_for('formulario'))
    
    @app.route('/clientes', methods=['GET', 'POST'])
    def clientes():
        if request.method == 'POST':
            nome = request.form['nome']
            endereco = request.form['endereco']
            telefone = request.form['telefone']
            email = request.form['email']

            novo_cliente = Cliente(nome=nome, endereco=endereco, telefone=telefone, email=email)
            db.session.add(novo_cliente)
            db.session.commit()
            return redirect(url_for('cliente'))
        return render_template('formulario.html')
    
    @app.route('/consultar', methods=['GET', POST])
    def cliente():
        if request.method == 'POST':
            nome = request.form['nome']
            clientes = Cliente.query.filter(Cliente.nome.like(f'%{nome}%')).all()
            return render_template('procurar.html', clientes=clientes)
        return render_template('clientes.html')
    
    @app.route('/exportar', methods=[POST])
    def exportar_clientes():
        nome = request.form['nome']
        clientes = Cliente.query.filter(Cliente.nome.like(f'%{nome}%')).all()

        dados = {
            'Nome': [cliente.nome for cliente in clientes],
            'Endereço': [cliente.endereco for cliente in clientes],
            'Telefone': [cliente.telefone for cliente in clientes],
            'Email' : [cliente.email for cliente in clientes],
        }
        df = pd.DataFrame(dados)

        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Clientes')
        writer.salve()
        output.seek(0)

        return send_file(output, attachment_filename="clientes.xlsx", as_attachment=True)
    if __name__ == '__main__':
        db.create_all()
        app.run(debug=True)