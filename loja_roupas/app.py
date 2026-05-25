#Ele configura o Flask, gera o banco de dados loja.db automaticamente e cria as rotas da API e da interface visual

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from database import db
from models import Funcionario, Produto

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

 # Endpoint de API para os testes automatizados
@app.route('/api/produto/<int:id>', methods=['PUT'])
def api_editar_produto(id):
    produto = Produto.query.get_or_404(id)
    data = request.get_json() or {}
 
    nome = data.get('nome')
    preco = data.get('preco')
    quantidade = data.get('quantidade')
 
    if not nome or preco is None or quantidade is None:
        return jsonify({'erro': 'Dados incompletos'}), 400
 
    produto.nome = nome
    produto.preco = float(preco)
    produto.quantidade = int(quantidade)
    db.session.commit()
 
    return jsonify({'mensagem': 'Produto atualizado com sucesso!'}), 200
 

# rota para cadastrar produtos
# o que a rota faz: abre a página /produto - recebe dados do forumulario - valida campos - salva no banco e mostra mensagem de sucesso
@app.route('/produto', methods=['GET', 'POST'])
def cadastro_produto():

    if request.method == 'POST':

        nome = request.form.get('nome')
        preco = request.form.get('preco')
        quantidade = request.form.get('quantidade')

        if not nome or not preco or not quantidade:
            flash('Preencha todos os campos!', 'erro')
            return redirect(url_for('cadastro_produto'))

        novo_produto = Produto(
            nome=nome,
            preco=float(preco),
            quantidade=int(quantidade)
        )

        db.session.add(novo_produto)
        db.session.commit()

        flash('Produto cadastrado com sucesso!', 'sucesso')
        return redirect(url_for('cadastro_produto'))

    return render_template('produto.html')
# Rota para editar um produto existente
# GET: abre o formulário pré-preenchido
# POST: salva as alterações no banco
@app.route('/produto/<int:id>/editar', methods=['GET', 'POST'])
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
 
    if request.method == 'POST':
        nome = request.form.get('nome')
        preco = request.form.get('preco')
        quantidade = request.form.get('quantidade')
 
        if not nome or not preco or not quantidade:
            flash('Preencha todos os campos!', 'erro')
            return redirect(url_for('editar_produto', id=id))
 
        produto.nome = nome
        produto.preco = float(preco)
        produto.quantidade = int(quantidade)
        db.session.commit()
 
        flash('Produto atualizado com sucesso!', 'sucesso')
        return redirect(url_for('home'))
 
    return render_template('editar_produto.html', produto=produto)


# Rota para deletar um produto existente
# POST: remove o produto do banco e volta para a home
@app.route('/produto/<int:id>/deletar', methods=['POST'])
def deletar_produto(id):
    produto = Produto.query.get_or_404(id)

    db.session.delete(produto)
    db.session.commit()

    flash('Produto deletado com sucesso!', 'sucesso')
    return redirect(url_for('home'))


# será nossa home para mostrar o painel administrativo do lojista 
@app.route('/')
def home():

    produtos = Produto.query.all()

    return render_template(
        'home.html',
        produtos=produtos
    )


if __name__ == '__main__':
    app.run(debug=True)
