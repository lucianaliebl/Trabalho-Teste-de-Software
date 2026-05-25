import pytest
from app import app, db
from models import Funcionario, Produto


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

        yield client

        with app.app_context():
            db.drop_all()


def test_cadastro_api_sucesso(client):
    """CT-01: Cadastro com sucesso via API"""

    dados = {
        "nome": "Lucas",
        "email": "lucas@loja.com",
        "senha": "senha_segura"
    }

    resposta = client.post('/api/cadastro', json=dados)

    assert resposta.status_code == 201
    assert "mensagem" in resposta.get_json()
    assert resposta.get_json()["mensagem"] == "Funcionário cadastrado com sucesso!"


def test_cadastro_api_email_duplicado(client):
    """CT-02: Erro ao tentar cadastrar e-mail duplicado"""

    dados = {
        "nome": "Ana",
        "email": "ana@loja.com",
        "senha": "123"
    }

    client.post('/api/cadastro', json=dados)

    resposta = client.post('/api/cadastro', json=dados)

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()
    assert resposta.get_json()["erro"] == "E-mail já cadastrado"


def test_criptografia_senha_unitario():
    """CT-UT-01: Validar a criptografia correta da senha do funcionário"""

    f = Funcionario()

    senha_puro_texto = "SenhaSegura123"

    f.set_senha(senha_puro_texto)

    assert f.senha_hash != senha_puro_texto
    assert f.senha_hash is not None

    from werkzeug.security import check_password_hash

    assert check_password_hash(
        f.senha_hash,
        senha_puro_texto
    ) is True


def test_cadastro_produto_sucesso(client):
    """CT-03: Cadastro de produto com sucesso"""

    dados = {
        "nome": "Camiseta Nike",
        "preco": "99.90",
        "quantidade": "10"
    }

    resposta = client.post(
        '/produto',
        data=dados,
        follow_redirects=True
    )

    assert resposta.status_code == 200

    assert b'Produto cadastrado com sucesso!' in resposta.data

    with app.app_context():

        produto = Produto.query.filter_by(
            nome="Camiseta Nike"
        ).first()

        assert produto is not None
        assert produto.preco == 99.90
        assert produto.quantidade == 10


def test_cadastro_produto_campos_vazios(client):
    """CT-04: Erro ao cadastrar produto com campos vazios"""

    dados = {
        "nome": "",
        "preco": "",
        "quantidade": ""
    }

    resposta = client.post(
        '/produto',
        data=dados,
        follow_redirects=True
    )

    assert resposta.status_code == 200

    assert b'Preencha todos os campos!' in resposta.data

    with app.app_context():

        produtos = Produto.query.all()

        assert len(produtos) == 0


# testes para editar produto
# ── helper: cria um produto diretamente no banco ──────────────────────────────
def criar_produto(nome="Camiseta Nike", preco=99.90, quantidade=10):
    """Insere um produto no banco e retorna o objeto criado."""
    produto = Produto(nome=nome, preco=preco, quantidade=quantidade)
    db.session.add(produto)
    db.session.commit()
    return produto


# ── Edição do produto com sucesso (interface web) ─────────────────────
def test_editar_produto_sucesso(client):
    """Editar produto com dados válidos deve atualizar o banco."""
    with app.app_context():
        produto = criar_produto()
        produto_id = produto.id

    dados = {
        "nome": "Camiseta Adidas",
        "preco": "149.90",
        "quantidade": "5"
    }
    resposta = client.post(
        f'/produto/{produto_id}/editar',
        data=dados,
        follow_redirects=True
    )

    assert resposta.status_code == 200

    with app.app_context():
        produto_atualizado = Produto.query.get(produto_id)
        assert produto_atualizado.nome == "Camiseta Adidas"
        assert produto_atualizado.preco == 149.90
        assert produto_atualizado.quantidade == 5


# ── edição com campos vazios deve exibir erro ─────────────────────────
def test_editar_produto_campos_vazios(client):
    """Campos vazios no formulário de edição devem exibir mensagem de erro."""
    with app.app_context():
        produto = criar_produto()
        produto_id = produto.id

    dados = {"nome": "", "preco": "", "quantidade": ""}
    resposta = client.post(
        f'/produto/{produto_id}/editar',
        data=dados,
        follow_redirects=True
    )

    assert resposta.status_code == 200
    assert b'Preencha todos os campos!' in resposta.data

    # Garante que os dados originais não foram alterados
    with app.app_context():
        produto_inalterado = Produto.query.get(produto_id)
        assert produto_inalterado.nome == "Camiseta Nike"
        assert produto_inalterado.preco == 99.90
        assert produto_inalterado.quantidade == 10


# ── edição de produto inexistente deve retornar 404 ───────────────────
def test_editar_produto_nao_encontrado(client):
    """Tentar editar um produto com ID inexistente deve retornar 404."""
    resposta = client.get('/produto/9999/editar')
    assert resposta.status_code == 404


