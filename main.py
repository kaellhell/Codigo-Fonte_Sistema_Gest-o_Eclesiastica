import tkinter as tk
import ttkbootstrap as tb
from tkinter import messagebox
import os
import sys
from PIL import Image, ImageTk

# 🚀 NOVAS BIBLIOTECAS PARA A ATUALIZAÇÃO AUTOMÁTICA
import requests
import threading
import webbrowser

from repository import SQLiteRepository
from logger import registrar_login
from telas.aba_membros import AbaMembros
from telas.aba_ministerios import AbaMinisterios
from telas.aba_relatorios import AbaRelatorios
from telas.aba_config import AbaConfig
from telas.aba_auditoria import AbaAuditoria

# ==============================================================
# 🌍 CÉREBRO DE ATUALIZAÇÃO (APONTA PARA O SEU GITHUB)
# ==============================================================
VERSAO_ATUAL = "1.0"
URL_VERSAO = "https://raw.githubusercontent.com/kaellhell/Atualizacoes_Gestao_Igreja/main/versao.txt"

def verificar_atualizacoes():
    def checar():
        try:
            # O sistema vai na internet ler o seu arquivo de texto silenciosamente
            resposta = requests.get(URL_VERSAO, timeout=5)
            dados = resposta.text.strip().split('|')
            
            if len(dados) == 2:
                versao_nuvem = dados[0]
                link_download = dados[1]

                # Se a versão do GitHub for maior, ele dispara o Alerta!
                if versao_nuvem > VERSAO_ATUAL:
                    msg = f"🎉 Uma nova atualização do Gestão Eclesiástica está disponível!\n\nVersão atual: {VERSAO_ATUAL}\nNova versão: {versao_nuvem}\n\nDeseja baixar a nova versão agora?"
                    if messagebox.askyesno("Atualização Disponível", msg):
                        webbrowser.open(link_download)
        except Exception as e:
            pass # Se o cliente estiver sem internet, ignora e abre o programa normal.

    # Roda em segundo plano para não travar a tela de login
    threading.Thread(target=checar, daemon=True).start()

# ==============================================================
# FERRAMENTA PARA O EMPACOTADOR (PyInstaller) ACHAR A LOGO
# ==============================================================
def resource_path(relative_path):
    """Pega o caminho absoluto para os recursos funcionarem no .exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ==============================================================
# SISTEMA PRINCIPAL
# ==============================================================
class SistemaIgrejaGUI:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.root.title(f"Gestão Eclesiástica Enterprise - Versão {VERSAO_ATUAL}")
        self.root.geometry("1000x600")
        self.root.state('zoomed') # Inicia tela cheia
        
        # Ícone da Janela (opcional, se o Windows deixar)
        try:
            self.root.iconbitmap(resource_path("logo.ico"))
        except:
            pass

        self.tentativas_falhas = 0 
        
        # 🚀 CHAMA O OLHEIRO DE ATUALIZAÇÕES ASSIM QUE O SISTEMA ABRE!
        verificar_atualizacoes()

        self.tela_login()

    def tela_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame_login = tb.Frame(self.root, padding=40)
        frame_login.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # 🖼️ Tenta carregar a Logo
        try:
            caminho_logo = resource_path("logo.png")
            img = Image.open(caminho_logo)
            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            tb.Label(frame_login, image=self.logo_img).pack(pady=(0, 20))
        except:
            tb.Label(frame_login, text="⛪", font=("Helvetica", 50)).pack(pady=(0, 10))

        tb.Label(frame_login, text="Acesso Restrito", font=("Helvetica", 24, "bold"), bootstyle="primary").pack(pady=(0, 20))

        tb.Label(frame_login, text="Utilizador:").pack(anchor="w")
        self.entry_usuario = tb.Entry(frame_login, width=35, font=("Helvetica", 12))
        self.entry_usuario.pack(pady=5, ipady=5)

        tb.Label(frame_login, text="Senha:").pack(anchor="w", pady=(10, 0))
        self.entry_senha = tb.Entry(frame_login, show="•", width=35, font=("Helvetica", 12))
        self.entry_senha.pack(pady=5, ipady=5)

        self.entry_senha.bind("<Return>", lambda e: self.fazer_login())

        tb.Button(frame_login, text="ENTRAR", command=self.fazer_login, bootstyle="success", width=33).pack(pady=20, ipady=5)

        self.entry_usuario.focus()

    def fazer_login(self):
        # 🛡️ SISTEMA ANTI-HACKER
        if self.tentativas_falhas >= 3:
            messagebox.showerror("Bloqueado", "Muitas tentativas falhadas. O sistema foi bloqueado por segurança. Reinicie o aplicativo.")
            self.root.destroy()
            return

        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()

        if not usuario or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return

        auth_data = self.db.autenticar(usuario, senha)

        if auth_data:
            self.tentativas_falhas = 0 
            cargo, primeiro_login = auth_data
            
            # 🚀 GATILHO DE AUDITORIA E E-MAIL!
            registrar_login(usuario)

            if primeiro_login == 1:
                self.tela_trocar_senha_obrigatoria(usuario, cargo)
            else:
                self.tela_dashboard(cargo, usuario)
        else:
            self.tentativas_falhas += 1
            tentativas_restantes = 3 - self.tentativas_falhas
            messagebox.showerror("Erro", f"Credenciais inválidas!\nTentativas restantes: {tentativas_restantes}")

    def tela_trocar_senha_obrigatoria(self, usuario, cargo):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame_troca = tb.Frame(self.root, padding=40)
        frame_troca.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tb.Label(frame_troca, text="⚠️ Redefinição Obrigatória", font=("Helvetica", 20, "bold"), bootstyle="warning").pack(pady=(0, 20))
        tb.Label(frame_troca, text="Como este é o seu primeiro acesso,\nvocê precisa criar uma senha pessoal e segura.", justify=tk.CENTER).pack(pady=(0, 20))

        tb.Label(frame_troca, text="Nova Senha:").pack(anchor="w")
        entry_nova_senha = tb.Entry(frame_troca, show="•", width=35, font=("Helvetica", 12))
        entry_nova_senha.pack(pady=5, ipady=5)

        tb.Label(frame_troca, text="Confirme a Nova Senha:").pack(anchor="w", pady=(10, 0))
        entry_confirma_senha = tb.Entry(frame_troca, show="•", width=35, font=("Helvetica", 12))
        entry_confirma_senha.pack(pady=5, ipady=5)

        def salvar_nova_senha():
            s1 = entry_nova_senha.get().strip()
            s2 = entry_confirma_senha.get().strip()

            if not s1 or not s2:
                messagebox.showwarning("Aviso", "Preencha todos os campos!")
                return
            if s1 != s2:
                messagebox.showerror("Erro", "As senhas não coincidem!")
                return
            if len(s1) < 6:
                messagebox.showwarning("Aviso", "A senha deve ter pelo menos 6 caracteres!")
                return

            self.db.atualizar_senha(usuario, s1)
            messagebox.showinfo("Sucesso", "Senha atualizada com sucesso!\nBem-vindo ao sistema.")
            self.tela_dashboard(cargo, usuario)

        tb.Button(frame_troca, text="SALVAR NOVA SENHA", command=salvar_nova_senha, bootstyle="success", width=33).pack(pady=20, ipady=5)

    def tela_dashboard(self, cargo, usuario):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame_topo = tb.Frame(self.root)
        frame_topo.pack(fill=tk.X, padx=20, pady=10)

        tb.Label(frame_topo, text=f"Gestão Eclesiástica | Logado como: {usuario.upper()} ({cargo.upper()})", font=("Helvetica", 14, "bold"), bootstyle="info").pack(side=tk.LEFT)
        tb.Button(frame_topo, text="Sair (Logout)", command=self.logout, bootstyle="danger outline").pack(side=tk.RIGHT)

        self.notebook = tb.Notebook(self.root, bootstyle="primary")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # ABAS COMUNS
        aba_mem = AbaMembros(self.notebook, self.db)
        self.notebook.add(aba_mem.frame, text=" 👥 Membros ")

        # ABAS DO ADMIN
        if cargo == "admin":
            aba_min = AbaMinisterios(self.notebook, self.db)
            self.notebook.add(aba_min.frame, text=" 🎵 Ministérios ")
            
            aba_rel = AbaRelatorios(self.notebook, self.db)
            self.notebook.add(aba_rel.frame, text=" 📊 Relatórios ")
            
            aba_cfg = AbaConfig(self.notebook, self.db)
            self.notebook.add(aba_cfg.frame, text=" ⚙️ Configurações ")
            
            # 🕵️‍♂️ ABA AUDITORIA
            aba_aud = AbaAuditoria(self.notebook)
            self.notebook.add(aba_aud.frame, text=" 🕵️‍♂️ Auditoria ")

    def logout(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            self.tela_login()

if __name__ == "__main__":
    db = SQLiteRepository()
    app = tb.Window(themename="cyborg")
    SistemaIgrejaGUI(app, db)
    app.mainloop()