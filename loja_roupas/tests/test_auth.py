import pytest
from app import app, db
from models import Funcionario

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
    
    # Usamos a função do Werkzeug para garantir que o hash é válido para aquela senha
    from werkzeug.security import check_password_hash
    assert check_password_hash(f.senha_hash, senha_puro_texto) is True