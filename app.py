import streamlit as st
import json
import hashlib
import os

DB_FILE = "supervisores.json"

# ==================================================
# Funções de banco de dados
# ==================================================

def carregar_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def autenticar(usuario, senha):
    db = carregar_db()
    if usuario in db and db[usuario]["senha"] == hash_senha(senha):
        return db[usuario]  # retorna dados do usuário
    return None

def cadastrar_supervisor(usuario, senha, tipo="supervisor"):
    db = carregar_db()
    if usuario in db:
        return False
    db[usuario] = {
        "senha": hash_senha(senha),
        "tipo": tipo
    }
    salvar_db(db)
    return True


# ==================================================
# Inicializar admin automaticamente (se não existir)
# ==================================================
def inicializar_admin():
    db = carregar_db()
    if "admin" not in db:
        db["admin"] = {
            "senha": hash_senha("admin123"),
            "tipo": "admin"
        }
        salvar_db(db)

inicializar_admin()


# ==================================================
# Streamlit
# ==================================================

st.set_page_config(page_title="Sistema Supervisores", page_icon="🛡️")

if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "tipo" not in st.session_state:
    st.session_state.tipo = None


# ==================================================
# Tela de Login
# ==================================================
def tela_login():
    st.title("🔐 Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        dados = autenticar(usuario, senha)
        if dados:
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.session_state.tipo = dados["tipo"]
            st.success(f"Bem-vindo, {usuario}!")
            st.rerun()
        else:
            st.error("Credenciais inválidas!")


# ==================================================
# Tela de Cadastro (restrita ao admin)
# ==================================================
def tela_cadastro():
    if st.session_state.tipo != "admin":
        st.error("🚫 Você não tem permissão para acessar esta página.")
        return

    st.title("➕ Criar novo usuário (Somente Admin)")

    novo_usuario = st.text_input("Novo usuário:")
    senha = st.text_input("Senha:", type="password")
    tipo = st.selectbox("Tipo de usuário:", ["supervisor", "admin"])

    if st.button("Cadastrar"):
        if cadastrar_supervisor(novo_usuario, senha, tipo):
            st.success(f"Usuário '{novo_usuario}' criado com sucesso.")
        else:
            st.error("Usuário já existe.")


# ==================================================
# Tela principal
# ==================================================
def tela_principal():
    st.sidebar.success(f"Logado como: {st.session_state.usuario} ({st.session_state.tipo})")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.usuario = None
        st.session_state.tipo = None
        st.rerun()

    st.title("🏢 Painel do Supervisor")
    st.write("Conteúdo disponível para todos os supervisores.")

    if st.session_state.tipo == "admin":
        st.subheader("⚙ Funções exclusivas do Administrador")
        st.write("Aqui você pode adicionar opções avançadas futuramente.")


# ==================================================
# Roteamento
# ==================================================
if not st.session_state.logado:
    escolha = st.sidebar.radio("Menu", ["Login"])
    tela_login()

else:
    menu = ["Dashboard"]
    
    if st.session_state.tipo == "admin":
        menu.append("Cadastrar usuário")

    escolha = st.sidebar.radio("Menu", menu)

    if escolha == "Dashboard":
        tela_principal()
    elif escolha == "Cadastrar usuário":
        tela_cadastro()
