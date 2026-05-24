# define a estrutura da tabela de funcionários no banco e lida com a segurança da senha de forma criptografada
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class Funcionario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

# define a estrutura da tabela de produtos do sistema com os seguintes atributos:
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)