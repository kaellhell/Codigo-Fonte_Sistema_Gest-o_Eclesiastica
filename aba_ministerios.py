import tkinter as tk
import ttkbootstrap as tb
from tkinter import messagebox

class AbaMinisterios:
    def __init__(self, parent, db):
        self.frame = tb.Frame(parent)
        self.db = db
        self.montar_layout()

    def montar_layout(self):
        # AQUI ESTAVA O VILÃO! Removi o padding=20 daqui!
        frame_vincular = tb.LabelFrame(self.frame, text=" 🛡️ Escalar Voluntário ")
        frame_vincular.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15, ipadx=20, ipady=20)
        
        tb.Label(frame_vincular, text="Selecione o Membro (Ativos):").pack(anchor="w", pady=(10, 5), padx=10)
        self.combo_membro_equipe = tb.Combobox(frame_vincular, width=30, state="readonly")
        self.combo_membro_equipe.pack(pady=5, padx=10)
        
        tb.Label(frame_vincular, text="Ministério:").pack(anchor="w", pady=(10, 5), padx=10)
        self.combo_ministerio_add = tb.Combobox(frame_vincular, width=30, state="readonly")
        self.combo_ministerio_add.pack(pady=5, padx=10)
        
        tb.Button(frame_vincular, text="➕ Adicionar", command=self.vincular_membro, bootstyle="success", width=28).pack(pady=20, padx=10)
        tb.Button(frame_vincular, text="🗑️ Remover", command=self.remover_da_equipe, bootstyle="danger-outline", width=28).pack(pady=5, padx=10)

        frame_direita = tb.Frame(self.frame)
        frame_direita.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        frame_filtro = tb.Frame(frame_direita)
        frame_filtro.pack(fill=tk.X, pady=(0, 10))
        
        tb.Label(frame_filtro, text="Filtrar por Ministério: ", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        self.combo_filtro_ministerio = tb.Combobox(frame_filtro, width=30, state="readonly")
        self.combo_filtro_ministerio.pack(side=tk.LEFT, padx=10)
        self.combo_filtro_ministerio.bind("<<ComboboxSelected>>", lambda e: self.atualizar_tabela_equipes())

        self.tabela_equipe = tb.Treeview(frame_direita, columns=("Nome", "Telefone"), show="headings", bootstyle="info")
        self.tabela_equipe.heading("Nome", text="Voluntário", anchor="w")
        self.tabela_equipe.column("Nome", anchor="w", width=250)
        self.tabela_equipe.heading("Telefone", text="Telefone", anchor="center")
        self.tabela_equipe.column("Telefone", anchor="center", width=150)
        self.tabela_equipe.pack(fill=tk.BOTH, expand=True)
        self.atualizar_combobox_equipes()

    def atualizar_combobox_equipes(self):
        self.combo_membro_equipe['values'] = self.db.listar_nomes_membros_ativos()
        ministerios = self.db.listar_ministerios()
        self.combo_ministerio_add['values'] = ministerios
        self.combo_filtro_ministerio['values'] = ministerios
        if ministerios:
            self.combo_filtro_ministerio.current(0)
            self.atualizar_tabela_equipes()

    def vincular_membro(self):
        membro = self.combo_membro_equipe.get()
        ministerio = self.combo_ministerio_add.get()
        if not membro or not ministerio: return
        try:
            self.db.vincular_equipe(membro, ministerio)
            messagebox.showinfo("Sucesso", f"{membro} adicionado!")
            self.combo_filtro_ministerio.set(ministerio)
            self.atualizar_tabela_equipes()
        except ValueError as e: 
            messagebox.showwarning("Erro", str(e))

    def remover_da_equipe(self):
        sel = self.tabela_equipe.selection()
        if not sel: return
        nome = self.tabela_equipe.item(sel[0], "values")[0]
        min_nome = self.combo_filtro_ministerio.get()
        if messagebox.askyesno("Confirmar", f"Remover '{nome}'?"):
            self.db.remover_da_equipe(nome, min_nome)
            self.atualizar_tabela_equipes()

    def atualizar_tabela_equipes(self):
        for l in self.tabela_equipe.get_children(): self.tabela_equipe.delete(l)
        ministerio = self.combo_filtro_ministerio.get()
        if not ministerio: return
        for nome, tel in self.db.buscar_equipe_por_ministerio(ministerio):
            self.tabela_equipe.insert("", tk.END, values=(nome, tel))