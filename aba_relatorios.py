import tkinter as tk
import ttkbootstrap as tb
import os
import webbrowser
import html  # 🛡️ O ESCUDO ANTI-HACKER PARA HTML!

class AbaRelatorios:
    def __init__(self, parent, db):
        self.frame = tb.Frame(parent)
        self.db = db
        self.montar_layout()

    def montar_layout(self):
        frame_botoes = tb.Frame(self.frame)
        frame_botoes.pack(expand=True, padx=50, pady=50) 
        
        tb.Label(frame_botoes, text="📄 Gerador de Relatórios", font=("Helvetica", 20, "bold"), bootstyle="primary").pack(pady=20)
        
        tb.Button(frame_botoes, text="1. Ficha Geral de Membros", command=self.gerar_relatorio_membros, bootstyle="info", width=40).pack(pady=10)
        tb.Button(frame_botoes, text="2. Escalas de Ministérios", command=self.gerar_relatorio_ministerios, bootstyle="warning", width=40).pack(pady=10)

    def gerar_relatorio_membros(self):
        membros = self.db.buscar_todos()
        html_content = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:Arial;margin:40px;background:#f4f7f6;}}.header{{text-align:center;padding:20px;background:#0052cc;color:white;}}table{{width:100%;border-collapse:collapse;background:white;}}th,td{{padding:12px;border-bottom:1px solid #ddd;}}th{{background:#f0f0f0;}}.Ativo{{color:green;}}.Visitante{{color:#d39e00;}}.Afastado{{color:red;}}@media print{{.btn-imprimir{{display:none;}}}}</style></head><body><div class="header"><h2>📋 Relatório Geral de Membros</h2></div><table><tr><th>Nome</th><th>Telefone</th><th>Nascimento</th><th>Batismo</th><th>Status</th></tr>"""
        
        for m in membros: 
            # 🛡️ SANITIZAÇÃO DE DADOS: Transforma scripts maliciosos em texto puro!
            nome_seguro = html.escape(m.nome)
            tel_seguro = html.escape(m.telefone)
            email_seguro = html.escape(m.email) if m.email else ""
            batismo_seguro = html.escape(m.data_batismo) if m.data_batismo else "-"
            
            html_content += f"""<tr><td>{nome_seguro}</td><td>{tel_seguro}</td><td>{m.data_nascimento}</td><td>{batismo_seguro}</td><td class="{m.status}">{m.status}</td></tr>"""
            
        html_content += """</table><br><button class="btn-imprimir" onclick="window.print()" style="padding:10px;background:#28a745;color:white;cursor:pointer;">🖨️ Imprimir PDF</button></body></html>"""
        
        caminho = os.path.abspath("relatorio_membros.html")
        with open(caminho, "w", encoding="utf-8") as f: f.write(html_content)
        webbrowser.open(f"file://{caminho}")

    def gerar_relatorio_ministerios(self):
        ministerios = self.db.listar_ministerios()
        html_content = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:Arial;margin:40px;background:#f4f7f6;}}.header{{text-align:center;padding:20px;background:#6f42c1;color:white;}}.box{{background:white;margin-top:20px;padding:20px;}}@media print{{.btn-imprimir{{display:none;}}}}</style></head><body><div class="header"><h2>🎵 Relatório de Ministérios</h2></div><button class="btn-imprimir" onclick="window.print()" style="padding:10px;background:#28a745;color:white;cursor:pointer;">🖨️ Imprimir PDF</button>"""
        
        for min_nome in ministerios:
            equipe = self.db.buscar_equipe_por_ministerio(min_nome)
            html_content += f"""<div class="box"><h3 style="color:#6f42c1;">{min_nome} ({len(equipe)} voluntários)</h3><ul>"""
            for nome, tel in equipe: 
                # 🛡️ SANITIZAÇÃO AQUI TAMBÉM!
                html_content += f"<li><strong>{html.escape(nome)}</strong> - {html.escape(tel)}</li>"
            html_content += "</ul></div>"
            
        html_content += "</body></html>"
        
        caminho = os.path.abspath("relatorio_ministerios.html")
        with open(caminho, "w", encoding="utf-8") as f: f.write(html_content)
        webbrowser.open(f"file://{caminho}")