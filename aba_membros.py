import tkinter as tk
import ttkbootstrap as tb 
from tkinter import messagebox, filedialog
import os
import shutil  
import webbrowser
import urllib.parse
from datetime import datetime, date
from PIL import Image, ImageTk  

from models import Membro
from exceptions import ContatoDuplicadoError, ContatoNaoEncontradoError

PASTA_FOTOS = "fotos_membros"
if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)

class AbaMembros:
    def __init__(self, parent, db, cargo, on_update_callback=None):
        self.frame = tb.Frame(parent)
        self.db = db
        self.cargo = cargo
        self.on_update_callback = on_update_callback 
        self.caminho_foto_atual = None
        self.nome_em_edicao = None  # <-- NOVA MEMÓRIA DO SISTEMA
        self.montar_layout()

    def montar_layout(self):
        frame_esquerda = tb.Frame(self.frame)
        frame_esquerda.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)

        card_foto = tb.LabelFrame(frame_esquerda, text=" 📸 Foto do Perfil ")
        card_foto.pack(fill=tk.X, pady=(0, 10), ipadx=10, ipady=10)

        self.label_foto = tb.Label(card_foto, width=35, text="Sem Foto", anchor="center", relief=tk.SUNKEN)
        self.label_foto.pack(pady=5)
        tb.Button(card_foto, text="Selecionar Imagem", command=self.escolher_foto, bootstyle="info-outline", width=25).pack(pady=5)

        card_dados = tb.LabelFrame(frame_esquerda, text=" 📋 Dados Cadastrais ")
        card_dados.pack(fill=tk.X, pady=(0, 10), ipadx=15, ipady=15)

        tb.Label(card_dados, text="Nome Completo:*").grid(row=0, column=0, columnspan=2, sticky="w", padx=10)
        self.entry_nome = tb.Entry(card_dados)
        self.entry_nome.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10), padx=10)

        tb.Label(card_dados, text="Telefone:*").grid(row=2, column=0, sticky="w", padx=10)
        tb.Label(card_dados, text="Nascimento:*").grid(row=2, column=1, sticky="w", padx=(0, 10))
        
        self.entry_tel = tb.Entry(card_dados)
        self.entry_tel.grid(row=3, column=0, sticky="ew", pady=(0, 10), padx=10)
        
        self.entry_nasc = tb.Entry(card_dados)
        self.entry_nasc.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))

        tb.Label(card_dados, text="Status:*").grid(row=4, column=0, sticky="w", padx=10)
        tb.Label(card_dados, text="Batismo:").grid(row=4, column=1, sticky="w", padx=(0, 10))
        
        self.combo_status = tb.Combobox(card_dados, values=["Ativo", "Visitante", "Afastado"], state="readonly")
        self.combo_status.grid(row=5, column=0, sticky="ew", pady=(0, 10), padx=10)
        
        self.entry_batismo = tb.Entry(card_dados)
        self.entry_batismo.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))

        tb.Label(card_dados, text="E-mail:").grid(row=6, column=0, columnspan=2, sticky="w", padx=10)
        self.entry_email = tb.Entry(card_dados)
        self.entry_email.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10)

        card_dados.columnconfigure(0, weight=1)
        card_dados.columnconfigure(1, weight=1)

        # ====== BOTÕES ATUALIZADOS ======
        frame_botoes = tb.Frame(frame_esquerda)
        frame_botoes.pack(fill=tk.X, pady=5)

        tb.Button(frame_botoes, text="💾 Novo", command=self.adicionar_membro, bootstyle="success", width=12).pack(side=tk.LEFT, padx=(0, 5))
        tb.Button(frame_botoes, text="✏️ Editar", command=self.atualizar_membro_selecionado, bootstyle="info", width=12).pack(side=tk.LEFT, padx=(0, 5))
        tb.Button(frame_botoes, text="🧹 Limpar", command=self.limpar_formulario, bootstyle="secondary-outline", width=10).pack(side=tk.LEFT)
        
        if self.cargo == "admin": 
            tb.Button(frame_botoes, text="🗑️", command=self.remover_membro, bootstyle="danger").pack(side=tk.RIGHT)

        # ================= LADO DIREITO =================
        frame_direita = tb.Frame(self.frame)
        frame_direita.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.frame_alertas = tb.LabelFrame(frame_direita, text=" 🎂 Radar de Aniversariantes (Próximos 3 Dias) ")
        self.frame_alertas.pack(fill=tk.X, pady=(0, 15), ipadx=10, ipady=10)
        
        self.container_alertas = tb.Frame(self.frame_alertas)
        self.container_alertas.pack(fill=tk.X, padx=10)
        
        tb.Label(frame_direita, text="💡 Dica: Clique para Editar, ou DUPLO CLIQUE para abrir o Perfil.", font=("Helvetica", 9, "italic")).pack(anchor="w", pady=(0, 5))

        colunas = ("Nome", "Telefone", "Nascimento", "Status")
        self.tabela = tb.Treeview(frame_direita, columns=colunas, show="headings", bootstyle="primary")
        
        self.tabela.heading("Nome", text="Nome", anchor="w")
        self.tabela.column("Nome", anchor="w", width=250)
        
        self.tabela.heading("Telefone", text="Telefone", anchor="center")
        self.tabela.column("Telefone", anchor="center", width=120)
        
        self.tabela.heading("Nascimento", text="Nascimento", anchor="center")
        self.tabela.column("Nascimento", anchor="center", width=100)
        
        self.tabela.heading("Status", text="Status", anchor="center")
        self.tabela.column("Status", anchor="center", width=100)
        
        self.tabela.pack(fill=tk.BOTH, expand=True)
        
        self.tabela.bind("<<TreeviewSelect>>", self.carregar_dados_no_formulario) 
        self.tabela.bind("<Double-1>", self.abrir_perfil_popup) 
        
        self.atualizar_tabela()

    def limpar_formulario(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_tel.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_nasc.delete(0, tk.END)
        self.entry_batismo.delete(0, tk.END)
        self.combo_status.set("")
        self.label_foto.config(image='', text="Sem Foto")
        self.caminho_foto_atual = None
        self.nome_em_edicao = None # Limpa a memória!

    def carregar_dados_no_formulario(self, event):
        sel = self.tabela.selection()
        if not sel: return
        nome_selecionado = self.tabela.item(sel[0], "values")[0]
        
        membro = next((m for m in self.db.buscar_todos() if m.nome == nome_selecionado), None)
        if not membro: return

        self.limpar_formulario()
        self.entry_nome.insert(0, membro.nome)
        self.entry_tel.insert(0, membro.telefone)
        if membro.email: self.entry_email.insert(0, membro.email)
        self.entry_nasc.insert(0, membro.data_nascimento)
        self.combo_status.set(membro.status)
        if membro.data_batismo: self.entry_batismo.insert(0, membro.data_batismo)

        self.nome_em_edicao = membro.nome # Salva na memória quem está sendo editado!

        if membro.foto_path and os.path.exists(membro.foto_path):
            img = Image.open(membro.foto_path)
            img = img.resize((250, 250), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.label_foto.config(image=img_tk, text="")
            self.label_foto.image = img_tk 
            self.caminho_foto_atual = membro.foto_path

    # ====== A MÁGICA DE ATUALIZAR O PERFIL ======
    def atualizar_membro_selecionado(self):
        if not self.nome_em_edicao:
            messagebox.showwarning("Aviso", "Selecione um membro na tabela primeiro para poder editar!")
            return
            
        try:
            batismo = self.entry_batismo.get() if self.entry_batismo.get().strip() != "" else None
            foto_salva = None
            
            if self.caminho_foto_atual:
                nome_arquivo = os.path.basename(self.caminho_foto_atual)
                foto_salva = os.path.join(PASTA_FOTOS, f"{self.entry_nome.get()}_{nome_arquivo}")
                if self.caminho_foto_atual != foto_salva: 
                    shutil.copy(self.caminho_foto_atual, foto_salva)
            
            membro_editado = Membro(self.entry_nome.get(), self.entry_tel.get(), self.entry_email.get(), self.entry_nasc.get(), self.combo_status.get(), batismo, foto_salva)
            
            self.db.atualizar_membro(membro_editado, self.nome_em_edicao)
            messagebox.showinfo("Sucesso", "Perfil atualizado com sucesso!")
            
            self.limpar_formulario()
            self.atualizar_tabela()
            if self.on_update_callback: self.on_update_callback()
            
        except ValueError as e: messagebox.showwarning("Erro", str(e))
        except ContatoDuplicadoError as e: messagebox.showerror("Erro", str(e))

    def abrir_perfil_popup(self, event):
        sel = self.tabela.selection()
        if not sel: return
        nome_selecionado = self.tabela.item(sel[0], "values")[0]
        membro = next((m for m in self.db.buscar_todos() if m.nome == nome_selecionado), None)
        if not membro: return

        janela = tb.Toplevel(self.frame)
        janela.title(f"Perfil Detalhado: {membro.nome}")
        janela.geometry("650x300")
        janela.transient(self.frame.winfo_toplevel()) 
        janela.grab_set() 

        frame_esq = tb.Frame(janela)
        frame_esq.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)

        lbl_foto = tb.Label(frame_esq, width=20, text="Sem Foto", relief=tk.SUNKEN, anchor="center")
        lbl_foto.pack()

        if membro.foto_path and os.path.exists(membro.foto_path):
            img = Image.open(membro.foto_path)
            img = img.resize((250, 250), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            lbl_foto.config(image=img_tk, text="")
            lbl_foto.image = img_tk 

        frame_dir = tb.Frame(janela)
        frame_dir.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=20)

        tb.Label(frame_dir, text=membro.nome, font=("Helvetica", 22, "bold"), bootstyle="primary").pack(anchor="w", pady=(0, 15))
        tb.Label(frame_dir, text=f"📞 {membro.telefone}", font=("Helvetica", 14)).pack(anchor="w", pady=2)
        tb.Label(frame_dir, text=f"📧 {membro.email or 'Não informado'}", font=("Helvetica", 14)).pack(anchor="w", pady=2)
        tb.Label(frame_dir, text=f"🎂 Nasc: {membro.data_nascimento}", font=("Helvetica", 14)).pack(anchor="w", pady=2)
        tb.Label(frame_dir, text=f"🕊️ Batismo: {membro.data_batismo or 'Não informado'}", font=("Helvetica", 14)).pack(anchor="w", pady=2)
        
        cor_status = "success" if membro.status == "Ativo" else ("warning" if membro.status == "Visitante" else "danger")
        tb.Label(frame_dir, text=f"📌 Status: {membro.status}", font=("Helvetica", 14, "bold"), bootstyle=cor_status).pack(anchor="w", pady=(15,0))

    def escolher_foto(self):
        caminho_arquivo = filedialog.askopenfilename(title="Escolha uma foto", filetypes=[("Imagens", "*.jpg *.jpeg *.png")])
        if caminho_arquivo:
            img = Image.open(caminho_arquivo)
            img = img.resize((250, 250), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.label_foto.config(image=img_tk, text="")
            self.label_foto.image = img_tk 
            self.caminho_foto_atual = caminho_arquivo 

    def atualizar_radar_aniversarios(self):
        for widget in self.container_alertas.winfo_children(): widget.destroy()
        membros = self.db.buscar_todos()
        hoje = date.today()
        achou_alguem = False

        for m in membros:
            try:
                nasc = datetime.strptime(m.data_nascimento, "%d/%m/%Y").date()
                niver_este_ano = date(hoje.year, nasc.month, nasc.day)
                if niver_este_ano < hoje: niver_este_ano = date(hoje.year + 1, nasc.month, nasc.day)
                dias_faltando = (niver_este_ano - hoje).days
                
                if 0 <= dias_faltando <= 3:
                    achou_alguem = True
                    texto_dia = "HOJE!" if dias_faltando == 0 else f"em {dias_faltando} dia(s)."
                    frame_linha = tb.Frame(self.container_alertas)
                    frame_linha.pack(fill=tk.X, pady=2)
                    tb.Label(frame_linha, text=f"🎉 {m.nome} faz aniversário {texto_dia}").pack(side=tk.LEFT)
                    tb.Button(frame_linha, text="📲 WhatsApp", bootstyle="success",
                              command=lambda telefone=m.telefone, nome=m.nome: self.abrir_whatsapp(telefone, nome)).pack(side=tk.RIGHT)
            except ValueError: pass 

        if not achou_alguem:
            tb.Label(self.container_alertas, text="Nenhum aniversariante nos próximos 3 dias.", bootstyle="secondary").pack(anchor="w")

    def abrir_whatsapp(self, telefone, nome):
        numero_limpo = ''.join(filter(str.isdigit, telefone))
        mensagem = f"A Paz do Senhor, {nome}! 🎉 O seu aniversário está chegando e a liderança se alegra muito com a sua vida! Que Deus te abençoe grandemente."
        msg_codificada = urllib.parse.quote(mensagem)
        link = f"https://wa.me/55{numero_limpo}?text={msg_codificada}"
        webbrowser.open(link)

    def adicionar_membro(self):
        try:
            batismo = self.entry_batismo.get() if self.entry_batismo.get().strip() != "" else None
            foto_salva = None
            if self.caminho_foto_atual:
                nome_arquivo = os.path.basename(self.caminho_foto_atual)
                foto_salva = os.path.join(PASTA_FOTOS, f"{self.entry_nome.get()}_{nome_arquivo}")
                if self.caminho_foto_atual != foto_salva: 
                    shutil.copy(self.caminho_foto_atual, foto_salva)
            
            novo_membro = Membro(self.entry_nome.get(), self.entry_tel.get(), self.entry_email.get(), self.entry_nasc.get(), self.combo_status.get(), batismo, foto_salva)
            self.db.salvar(novo_membro)
            messagebox.showinfo("Sucesso", "Ficha salva com sucesso!")
            self.limpar_formulario()
            self.atualizar_tabela()
            if self.on_update_callback: self.on_update_callback()
        except ValueError as e: messagebox.showwarning("Erro", str(e))
        except ContatoDuplicadoError as e: messagebox.showerror("Erro", str(e))

    def remover_membro(self):
        sel = self.tabela.selection()
        if not sel: return
        nome = self.tabela.item(sel, "values")[0]
        if messagebox.askyesno("Confirmar", f"Excluir '{nome}'?"):
            self.db.deletar(nome)
            self.limpar_formulario()
            self.atualizar_tabela()
            if self.on_update_callback: self.on_update_callback()

    def atualizar_tabela(self):
        for l in self.tabela.get_children(): self.tabela.delete(l)
        for m in self.db.buscar_todos():
            self.tabela.insert("", tk.END, values=(m.nome, m.telefone, m.data_nascimento, m.status))
        self.atualizar_radar_aniversarios()