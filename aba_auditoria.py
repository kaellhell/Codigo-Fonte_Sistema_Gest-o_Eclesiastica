import tkinter as tk
import ttkbootstrap as tb
import os

class AbaAuditoria:
    def __init__(self, parent):
        self.frame = tb.Frame(parent)
        self.montar_layout()

    def montar_layout(self):
        frame_topo = tb.Frame(self.frame)
        frame_topo.pack(fill=tk.X, padx=15, pady=15)
        
        tb.Label(frame_topo, text="🕵️‍♂️ Logs de Auditoria do Sistema", font=("Helvetica", 18, "bold"), bootstyle="primary").pack(side=tk.LEFT)
        tb.Button(frame_topo, text="🔄 Atualizar Logs", command=self.carregar_logs, bootstyle="info").pack(side=tk.RIGHT)

        frame_texto = tb.Frame(self.frame)
        frame_texto.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        self.texto_logs = tb.Text(frame_texto, wrap=tk.WORD, font=("Courier", 10), state=tk.DISABLED, bg="#1e1e1e", fg="#00ff00")
        self.texto_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tb.Scrollbar(frame_texto, command=self.texto_logs.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.texto_logs.config(yscrollcommand=scrollbar.set)

        self.carregar_logs()

    def carregar_logs(self):
        self.texto_logs.config(state=tk.NORMAL)
        self.texto_logs.delete(1.0, tk.END)
        
        if os.path.exists("sistema_auditoria.log"):
            with open("sistema_auditoria.log", "r", encoding="utf-8") as file:
                linhas = file.readlines()
                # Mostra as ações mais recentes no topo
                for linha in reversed(linhas):
                    self.texto_logs.insert(tk.END, linha)
        else:
            self.texto_logs.insert(tk.END, "Nenhum registo encontrado ainda.")
            
        self.texto_logs.config(state=tk.DISABLED)