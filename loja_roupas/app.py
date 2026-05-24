#Ele configura o Flask, gera o banco de dados loja.db automaticamente e cria as rotas da API e da interface visual

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from database import db
from models import Funcionario

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loja.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave-secreta-bem-segura'

db.init_app(app)

# Cria o banco SQLite e as tabelas se não existirem
with app.app_context():
    db.create_all()

# Rota para renderizar o formulário web na tela
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro_view():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not nome or not email or not senha:
            flash('Preencha todos os campos!', 'erro')
            return redirect(url_for('cadastro_view'))
            
        usuario_existente = Funcionario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('E-mail já cadastrado!', 'erro')
            return redirect(url_for('cadastro_view'))
            
        novo_funcionario = Funcionario(nome=nome, email=email)
        novo_funcionario.set_senha(senha)
        
        db.session.add(novo_funcionario)
        db.session.commit()
        
        flash('Funcionário cadastrado com sucesso!', 'sucesso')
        return redirect(url_for('cadastro_view'))
        
    return render_template('cadastro.html')

# Endpoint de API para os testes automatizados
@app.route('/api/cadastro', methods=['POST'])
def api_cadastro():
    data = request.get_json() or {}
    if 'nome' not in data or 'email' not in data or 'senha' not in data:
        return jsonify({'erro': 'Dados incompletos'}), 400
        
    if Funcionario.query.filter_by(email=data['email']).first():
        return jsonify({'erro': 'E-mail já cadastrado'}), 400
        
    novo = Funcionario(nome=data['nome'], email=data['email'])
    novo.set_senha(data['senha'])
    
    db.session.add(novo)
    db.session.commit()
    
    return jsonify({'mensagem': 'Funcionário cadastrado com sucesso!'}), 201

if __name__ == '__main__':
    app.run(debug=True)