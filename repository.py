import sqlite3
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from models import Membro
from exceptions import ContatoDuplicadoError, ContatoNaoEncontradoError
from logger import registrar_acao

class IMembroRepository(ABC):
    @abstractmethod
    def salvar(self, membro: Membro) -> None: pass
    @abstractmethod
    def deletar(self, nome: str) -> None: pass
    @abstractmethod
    def buscar_todos(self) -> List[Membro]: pass
    @abstractmethod
    def atualizar_membro(self, membro: Membro, nome_antigo: str) -> None: pass
    @abstractmethod
    def autenticar(self, username: str, senha: str) -> Optional[Tuple[str, int]]: pass
    @abstractmethod
    def atualizar_senha(self, username: str, nova_senha: str) -> None: pass
    @abstractmethod
    def listar_usuarios(self) -> List[str]: pass
    @abstractmethod
    def criar_usuario(self, username: str, senha_provisoria: str, role: str) -> None: pass
    @abstractmethod
    def deletar_usuario(self, username: str) -> None: pass
    
    # NOVAS FUNÇÕES PARA CONFIGURAÇÃO DE E-MAIL
    @abstractmethod
    def salvar_config(self, chave: str, valor: str) -> None: pass
    @abstractmethod
    def buscar_config(self, chave: str) -> str: pass

class SQLiteRepository(IMembroRepository):
    def __init__(self, db_name: str = "igreja_producao.db"):
        self.conn = sqlite3.connect(db_name)
        self._criar_tabelas()

    def _hash_senha(self, senha: str) -> str:
        chave_secreta = "#G3st40_Ent3rpr1s3_2026!"
        senha_temperada = senha + chave_secreta
        return hashlib.sha256(senha_temperada.encode('utf-8')).hexdigest()

    def _criar_tabelas(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS membros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    telefone TEXT NOT NULL,
                    email TEXT,
                    data_nascimento TEXT NOT NULL,
                    status TEXT NOT NULL,
                    data_batismo TEXT,
                    foto_path TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    senha_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    primeiro_login INTEGER DEFAULT 1
                )
            """)
            self.conn.execute("CREATE TABLE IF NOT EXISTS ministerios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE NOT NULL)")
            self.conn.execute("CREATE TABLE IF NOT EXISTS membros_ministerios (id INTEGER PRIMARY KEY AUTOINCREMENT, membro_nome TEXT NOT NULL, ministerio_nome TEXT NOT NULL, UNIQUE(membro_nome, ministerio_nome))")
            
            # 🚀 TABELA DE CONFIGURAÇÕES PARA O E-MAIL!
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS configuracoes (
                    chave TEXT PRIMARY KEY,
                    valor TEXT
                )
            """)
            
            self._criar_usuarios_padrao()
            self._popular_ministerios_padrao()

    def _criar_usuarios_padrao(self):
        with self.conn:
            cursor = self.conn.execute("SELECT COUNT(*) FROM usuarios")
            if cursor.fetchone()[0] == 0:
                self.conn.execute("INSERT INTO usuarios (username, senha_hash, role, primeiro_login) VALUES (?, ?, ?, 1)", ("admin", self._hash_senha("admin123"), "admin"))
                self.conn.execute("INSERT INTO usuarios (username, senha_hash, role, primeiro_login) VALUES (?, ?, ?, 1)", ("sec", self._hash_senha("sec123"), "secretario"))

    def _popular_ministerios_padrao(self):
        for min_nome in ["Louvor", "Kids", "Recepção", "Mídia", "Diaconia", "Jovens"]:
            try:
                with self.conn: self.conn.execute("INSERT INTO ministerios (nome) VALUES (?)", (min_nome,))
            except sqlite3.IntegrityError: pass

    # ====== SALVAR DADOS DO SISTEMA (E-MAIL) ======
    def salvar_config(self, chave: str, valor: str) -> None:
        with self.conn:
            self.conn.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)", (chave, valor))

    def buscar_config(self, chave: str) -> str:
        cursor = self.conn.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
        row = cursor.fetchone()
        return row[0] if row else ""

    # ====== GESTÃO DE USUÁRIOS ======
    def criar_usuario(self, username: str, senha_provisoria: str, role: str) -> None:
        try:
            with self.conn:
                self.conn.execute("INSERT INTO usuarios (username, senha_hash, role, primeiro_login) VALUES (?, ?, ?, 1)", 
                                  (username, self._hash_senha(senha_provisoria), role))
                registrar_acao(f"Criou um novo utilizador no sistema: {username} ({role})")
        except sqlite3.IntegrityError:
            raise ValueError(f"O utilizador '{username}' já existe no sistema!")

    def deletar_usuario(self, username: str) -> None:
        with self.conn:
            cursor = self.conn.execute("DELETE FROM usuarios WHERE username = ?", (username,))
            if cursor.rowcount == 0:
                raise ValueError(f"Utilizador '{username}' não encontrado.")
            registrar_acao(f"Apagou o utilizador do sistema: {username}")

    def autenticar(self, username: str, senha_digitada: str) -> Optional[Tuple[str, int]]:
        cursor = self.conn.execute("SELECT role, primeiro_login FROM usuarios WHERE username = ? AND senha_hash = ?", (username, self._hash_senha(senha_digitada)))
        row = cursor.fetchone()
        return (row[0], row[1]) if row else None

    def atualizar_senha(self, username: str, nova_senha: str) -> None:
        with self.conn:
            self.conn.execute("UPDATE usuarios SET senha_hash = ?, primeiro_login = 0 WHERE username = ?", (self._hash_senha(nova_senha), username))
            registrar_acao(f"Atualizou a senha do utilizador: {username}")

    def listar_usuarios(self) -> List[str]:
        cursor = self.conn.execute("SELECT username FROM usuarios")
        return [row[0] for row in cursor.fetchall()]

    # ====== GESTÃO DE MEMBROS E MINISTÉRIOS ======
    def salvar(self, membro: Membro) -> None:
        try:
            with self.conn: 
                self.conn.execute("INSERT INTO membros (nome, telefone, email, data_nascimento, status, data_batismo, foto_path) VALUES (?, ?, ?, ?, ?, ?, ?)", (membro.nome, membro.telefone, membro.email, membro.data_nascimento, membro.status, membro.data_batismo, membro.foto_path))
                registrar_acao(f"Cadastrou a Ficha do membro: {membro.nome}")
        except sqlite3.IntegrityError: 
            raise ContatoDuplicadoError(f"Erro: O membro '{membro.nome}' já está cadastrado!")

    def atualizar_membro(self, membro: Membro, nome_antigo: str) -> None:
        try:
            with self.conn:
                self.conn.execute("""
                    UPDATE membros 
                    SET nome=?, telefone=?, email=?, data_nascimento=?, status=?, data_batismo=?, foto_path=?
                    WHERE nome=?
                """, (membro.nome, membro.telefone, membro.email, membro.data_nascimento, membro.status, membro.data_batismo, membro.foto_path, nome_antigo))
                
                if membro.nome != nome_antigo:
                    self.conn.execute("UPDATE membros_ministerios SET membro_nome = ? WHERE membro_nome = ?", (membro.nome, nome_antigo))
                
                registrar_acao(f"Atualizou a Ficha do membro: {membro.nome}")
        except sqlite3.IntegrityError:
            raise ContatoDuplicadoError(f"Erro: Já existe outra pessoa com o nome '{membro.nome}'!")

    def deletar(self, nome: str) -> None:
        with self.conn:
            cursor = self.conn.execute("DELETE FROM membros WHERE nome = ?", (nome,))
            self.conn.execute("DELETE FROM membros_ministerios WHERE membro_nome = ?", (nome,))
            if cursor.rowcount == 0: 
                raise ContatoNaoEncontradoError(f"Membro '{nome}' não existe no banco.")
            registrar_acao(f"Deletou a Ficha do membro: {nome}")

    def buscar_todos(self) -> List[Membro]:
        cursor = self.conn.execute("SELECT nome, telefone, email, data_nascimento, status, data_batismo, foto_path FROM membros")
        return [Membro(nome=r[0], telefone=r[1], email=r[2], data_nascimento=r[3], status=r[4], data_batismo=r[5], foto_path=r[6]) for r in cursor.fetchall()]

    def listar_nomes_membros_ativos(self) -> List[str]:
        return [row[0] for row in self.conn.execute("SELECT nome FROM membros WHERE status = 'Ativo'").fetchall()]

    def listar_ministerios(self) -> List[str]:
        return [row[0] for row in self.conn.execute("SELECT nome FROM ministerios").fetchall()]

    def vincular_equipe(self, membro_nome: str, ministerio_nome: str):
        try:
            with self.conn: 
                self.conn.execute("INSERT INTO membros_ministerios (membro_nome, ministerio_nome) VALUES (?, ?)", (membro_nome, ministerio_nome))
                registrar_acao(f"Adicionou '{membro_nome}' ao Ministério de '{ministerio_nome}'")
        except sqlite3.IntegrityError: 
            raise ValueError(f"O membro '{membro_nome}' já faz parte do Ministério de {ministerio_nome}.")

    def remover_da_equipe(self, membro_nome: str, ministerio_nome: str):
        with self.conn: 
            self.conn.execute("DELETE FROM membros_ministerios WHERE membro_nome = ? AND ministerio_nome = ?", (membro_nome, ministerio_nome))
            registrar_acao(f"Removeu '{membro_nome}' do Ministério de '{ministerio_nome}'")

    def buscar_equipe_por_ministerio(self, ministerio_nome: str) -> List[tuple]:
        return self.conn.execute("SELECT m.nome, m.telefone FROM membros m JOIN membros_ministerios mm ON m.nome = mm.membro_nome WHERE mm.ministerio_nome = ?", (ministerio_nome,)).fetchall()