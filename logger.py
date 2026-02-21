import logging
import smtplib
import sqlite3
from email.mime.text import MIMEText
from datetime import datetime
import threading

logger = logging.getLogger("Auditoria")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("sistema_auditoria.log", encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

USUARIO_LOGADO = "Desconhecido"

def set_usuario_logado(usuario):
    global USUARIO_LOGADO
    USUARIO_LOGADO = usuario

def registrar_acao(acao):
    mensagem = f"[{USUARIO_LOGADO.upper()}] {acao}"
    logger.info(mensagem)

def enviar_email_login(usuario):
    """Envia um email buscando as credenciais do Banco de Dados"""
    data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    assunto = f"🚨 Alerta de Login: {usuario.upper()}"
    corpo = f"O utilizador '{usuario.upper()}' acabou de fazer login no Sistema de Gestão Eclesiástica.\nData e Hora do acesso: {data_hora}\n\nSe não reconheces este acesso, verifica o sistema imediatamente!"
    
    def enviar():
        try:
            # Puxa as configurações diretamente do banco de dados!
            conn = sqlite3.connect("igreja_producao.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT valor FROM configuracoes WHERE chave='email_remetente'")
            rem = cursor.fetchone()
            cursor.execute("SELECT valor FROM configuracoes WHERE chave='senha_app'")
            pwd = cursor.fetchone()
            cursor.execute("SELECT valor FROM configuracoes WHERE chave='email_destino'")
            dest = cursor.fetchone()
            conn.close()

            EMAIL_REMETENTE = rem[0] if rem else ""
            SENHA_APP = pwd[0] if pwd else ""
            EMAIL_DESTINO = dest[0] if dest else ""

            # Se o cliente não preencheu na tela de configs, o sistema aborta o envio silenciosamente.
            if not EMAIL_REMETENTE or not SENHA_APP or not EMAIL_DESTINO:
                return

            msg = MIMEText(corpo)
            msg['Subject'] = assunto
            msg['From'] = EMAIL_REMETENTE
            msg['To'] = EMAIL_DESTINO
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_REMETENTE, SENHA_APP)
            server.sendmail(EMAIL_REMETENTE, [EMAIL_DESTINO], msg.as_string())
            server.quit()
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
            
    threading.Thread(target=enviar).start()

def registrar_login(usuario):
    set_usuario_logado(usuario)
    registrar_acao("FEZ LOGIN NO SISTEMA.")
    enviar_email_login(usuario)