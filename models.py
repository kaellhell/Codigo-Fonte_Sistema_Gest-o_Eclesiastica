from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Membro:
    nome: str
    telefone: str
    email: str
    data_nascimento: str
    status: str  # Ex: "Ativo", "Visitante", "Afastado"
    data_batismo: Optional[str] = None # Optional porque visitantes não têm data de batismo
    foto_path: Optional[str] = None    # O caminho da foto no computador (ex: C:/fotos/joao.png)

    def __post_init__(self):
        
        # 1. Valida o Nome (Primeira letra maiúscula e exige sobrenome)
        self.nome = self.nome.strip().title()
        if len(self.nome.split()) < 2:
            raise ValueError(f"O nome '{self.nome}' é inválido! Insira nome e sobrenome.")

        # 2. Valida o E-mail (Se a pessoa não tiver, podemos deixar passar vazio, senão valida)
        self.email = self.email.strip().lower().replace(" ", "")
        if self.email and ("@" not in self.email or "." not in self.email):
            raise ValueError(f"O e-mail '{self.email}' é inválido!")

        # 3. Formata o Telefone ((DD) XXXXX-XXXX)
        telefone_limpo = ''.join(filter(str.isdigit, self.telefone))
        if len(telefone_limpo) not in [10, 11]:
            raise ValueError("O telefone deve ter 10 ou 11 dígitos (com DDD).")
        
        ddd = telefone_limpo[:2]
        numero = telefone_limpo[2:]
        if len(numero) == 9:
            self.telefone = f"({ddd}) {numero[:5]}-{numero[5:]}"
        else:
            self.telefone = f"({ddd}) {numero[:4]}-{numero[4:]}"

        # 4. Valida as Datas (Nascimento e Batismo)
        # Tenta converter a string "DD/MM/AAAA" para uma Data Real do calendário
        try:
            datetime.strptime(self.data_nascimento, "%d/%m/%Y")
        except ValueError:
            raise ValueError(f"A data de nascimento '{self.data_nascimento}' é inválida! Use o formato DD/MM/AAAA.")
            
        if self.data_batismo: # Só valida se a pessoa tiver preenchido a data de batismo
            try:
                datetime.strptime(self.data_batismo, "%d/%m/%Y")
            except ValueError:
                raise ValueError(f"A data de batismo '{self.data_batismo}' é inválida! Use o formato DD/MM/AAAA.")

        # 5. Valida o Status (Não deixa cadastrar status inventado)
        status_permitidos = ["Ativo", "Visitante", "Afastado"]
        self.status = self.status.strip().title()
        if self.status not in status_permitidos:
            raise ValueError(f"O status '{self.status}' é inválido! Escolha entre: Ativo, Visitante ou Afastado.")