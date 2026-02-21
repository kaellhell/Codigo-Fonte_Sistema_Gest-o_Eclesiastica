import tkinter as tk
import ttkbootstrap as tb
from tkinter import messagebox

class AbaConfig:
    def __init__(self, parent, db):
        self.frame = tb.Frame(parent)
        self.db = db
        self.montar_layout()

    def montar_layout(self):
        frame_esquerda = tb.Frame(self.frame)
        frame_esquerda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        frame_direita = tb.Frame(self.frame)
        frame_direita.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ================= CARD 1: CRIAR UTILIZADOR =================
        card_criar = tb.LabelFrame(frame_esquerda, text=" ➕ Criar Novo Utilizador ")
        card_criar.pack(fill=tk.X, pady=(0, 15), ipadx=15, ipady=15)
        
        tb.Label(card_criar, text="Nome de Utilizador (Login):").pack(anchor="w", pady=(5, 0), padx=10)
        self.entry_novo_user = tb.Entry(card_criar, width=30)
        self.entry_novo_user.pack(fill=tk.X, pady=5, padx=10)
        
        tb.Label(card_criar, text="Senha Provisória:").pack(anchor="w", pady=(5, 0), padx=10)
        self.entry_nova_senha = tb.Entry(card_criar, show="•", width=30)
        self.entry_nova_senha.pack(fill=tk.X, pady=5, padx=10)
        
        tb.Label(card_criar, text="Nível de Acesso (Cargo):").pack(anchor="w", pady=(5, 0), padx=10)
        self.combo_cargo = tb.Combobox(card_criar, values=["admin", "secretario"], state="readonly", width=28)
        self.combo_cargo.pack(fill=tk.X, pady=5, padx=10)
        
        tb.Button(card_criar, text="Salvar Utilizador", command=self.criar_usuario, bootstyle="success").pack(pady=(15, 5), padx=10, fill=tk.X)

        # ================= CARD 2: REMOVER UTILIZADOR =================
        card_remover = tb.LabelFrame(frame_esquerda, text=" 🗑️ Remover Utilizador ")
        card_remover.pack(fill=tk.X, pady=(0, 15), ipadx=15, ipady=15)
        
        tb.Label(card_remover, text="Selecione o Utilizador para DELETAR:").pack(anchor="w", pady=(5, 0), padx=10)
        self.combo_usuarios_del = tb.Combobox(card_remover, state="readonly", width=28)
        self.combo_usuarios_del.pack(fill=tk.X, pady=5, padx=10)
        
        tb.Button(card_remover, text="Deletar Utilizador", command=self.deletar_usuario, bootstyle="danger").pack(pady=(15, 5), padx=10, fill=tk.X)

        # ================= CARD 3: FORÇAR TROCA DE SENHA =================
        card_senha = tb.LabelFrame(frame_direita, text=" 🔑 Forçar Troca de Senha ")
        card_senha.pack(fill=tk.X, pady=(0, 15), ipadx=15, ipady=15)
        
        tb.Label(card_senha, text="Selecione o Utilizador:").pack(anchor="w", padx=10)
        self.combo_usuarios_senha = tb.Combobox(card_senha, state="readonly", width=30)
        self.combo_usuarios_senha.pack(fill=tk.X, pady=5, padx=10)
        
        tb.Label(card_senha, text="Digite a Nova Senha:").pack(anchor="w", pady=(10, 0), padx=10)
        self.entry_senha_admin_forca = tb.Entry(card_senha, show="•", width=30)
        self.entry_senha_admin_forca.pack(fill=tk.X, pady=5, padx=10)

        tb.Button(card_senha, text="Salvar Nova Senha", command=self.forcar_troca_senha, bootstyle="warning").pack(pady=(15, 5), padx=10, fill=tk.X)

        # ================= CARD 4: ALERTA DE E-MAIL (NOVO) =================
        card_email = tb.LabelFrame(frame_direita, text=" 📧 Alertas de Acesso (E-mail) ")
        card_email.pack(fill=tk.X, pady=(0, 15), ipadx=15, ipady=15)

        tb.Label(card_email, text="E-mail Remetente (Conta que vai enviar):").pack(anchor="w", padx=10)
        self.entry_email_remetente = tb.Entry(card_email, width=30)
        self.entry_email_remetente.pack(fill=tk.X, pady=5, padx=10)
        
        tb.Label(card_email, text="Senha de App (16 letras do Google):").pack(anchor="w", padx=10)
        self.entry_senha_app = tb.Entry(card_email, show="•", width=30)
        self.entry_senha_app.pack(fill=tk.X, pady=5, padx=10)
        
        tb.Label(card_email, text="E-mail de Destino (Pastor/Admin):").pack(anchor="w", padx=10)
        self.entry_email_destino = tb.Entry(card_email, width=30)
        self.entry_email_destino.pack(fill=tk.X, pady=5, padx=10)
        
        tb.Button(card_email, text="💾 Salvar E-mail", command=self.salvar_configs_email, bootstyle="info").pack(pady=(15, 5), padx=10, fill=tk.X)

        self.atualizar_combos_usuarios()
        self.carregar_configs_email()

    # ================= MÁGICA DOS BOTÕES =================
    def carregar_configs_email(self):
        self.entry_email_remetente.insert(0, self.db.buscar_config("email_remetente"))
        self.entry_senha_app.insert(0, self.db.buscar_config("senha_app"))
        self.entry_email_destino.insert(0, self.db.buscar_config("email_destino"))

    def salvar_configs_email(self):
        self.db.salvar_config("email_remetente", self.entry_email_remetente.get().strip())
        self.db.salvar_config("senha_app", self.entry_senha_app.get().strip())
        self.db.salvar_config("email_destino", self.entry_email_destino.get().strip())
        messagebox.showinfo("Sucesso", "Configurações de E-mail atualizadas e ativadas no banco de dados!")

    def atualizar_combos_usuarios(self):
        usuarios = self.db.listar_usuarios()
        self.combo_usuarios_del['values'] = usuarios
        self.combo_usuarios_senha['values'] = usuarios

    def criar_usuario(self):
        user = self.entry_novo_user.get().strip()
        senha = self.entry_nova_senha.get().strip()
        cargo = self.combo_cargo.get()
        if not user or not senha or not cargo:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
        try:
            self.db.criar_usuario(user, senha, cargo)
            messagebox.showinfo("Sucesso", f"Utilizador '{user}' criado com sucesso!\n\nEle será obrigado a criar uma senha pessoal no primeiro login.")
            self.entry_novo_user.delete(0, tk.END)
            self.entry_nova_senha.delete(0, tk.END)
            self.combo_cargo.set("")
            self.atualizar_combos_usuarios()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def deletar_usuario(self):
        user = self.combo_usuarios_del.get()
        if not user:
            messagebox.showwarning("Aviso", "Selecione um utilizador para deletar.")
            return
        if user == "admin":
            messagebox.showerror("Erro de Segurança", "O utilizador 'admin' raiz é blindado e não pode ser deletado do sistema!")
            return
        if messagebox.askyesno("Atenção EXTREMA", f"Tem a certeza absoluta que deseja DELETAR o acesso de '{user}' permanentemente?"):
            try:
                self.db.deletar_usuario(user)
                messagebox.showinfo("Sucesso", f"O utilizador '{user}' foi deletado e não tem mais acesso ao sistema.")
                self.combo_usuarios_del.set("")
                self.atualizar_combos_usuarios()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

    def forcar_troca_senha(self):
        usuario_selecionado = self.combo_usuarios_senha.get()
        nova_senha = self.entry_senha_admin_forca.get()
        if not usuario_selecionado or not nova_senha:
            messagebox.showwarning("Aviso", "Preencha o utilizador e a nova senha.")
            return
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja alterar a senha de '{usuario_selecionado}'?"):
            self.db.atualizar_senha(usuario_selecionado, nova_senha)
            messagebox.showinfo("Sucesso", f"A senha de {usuario_selecionado} foi atualizada!")
            self.combo_usuarios_senha.set("")
            self.entry_senha_admin_forca.delete(0, tk.END)