# Instalação do Projeto Telmoz

Este documento descreve as dependências e comandos necessários para executar o projeto Telmoz noutra máquina.

---

## Pré-requisitos

- **Python 3.8** ou superior
- Ligação à internet (para instalar dependências)

Para verificar a versão do Python:
```bash
python --version
```

---

## Dependências

O ficheiro `requirements.txt` contém todas as dependências:

| Pacote | Versão | Descrição |
|--------|--------|-----------|
| Flask | 3.0.0 | Framework web |
| Flask-SQLAlchemy | 3.1.1 | ORM para base de dados |
| Flask-Login | 0.6.3 | Gestão de sessões de administrador |
| Werkzeug | 3.0.1 | Utilitários WSGI |

---

## Comandos de Instalação

### Windows (PowerShell ou CMD)

```powershell
# 1. Navegar até à pasta do projeto
cd "C:\caminho\para\Telmoz 2.0"

# 2. Criar ambiente virtual (recomendado)
python -m venv venv

# 3. Ativar o ambiente virtual
venv\Scripts\activate

# 4. Instalar as dependências
pip install -r requirements.txt

# 5. Executar a aplicação
python app.py
```

### Linux / macOS (Terminal)

```bash
# 1. Navegar até à pasta do projeto
cd /caminho/para/Telmoz\ 2.0

# 2. Criar ambiente virtual (recomendado)
python3 -m venv venv

# 3. Ativar o ambiente virtual
source venv/bin/activate

# 4. Instalar as dependências
pip install -r requirements.txt

# 5. Executar a aplicação
python app.py
```

---

## Instalação sem ambiente virtual

Se preferir instalar globalmente (não recomendado):

```bash
pip install -r requirements.txt
python app.py
```

---

## Após a instalação

1. Aceda ao site em: **http://127.0.0.1:5000**
2. A base de dados SQLite (`telmoz.db`) é criada automaticamente na primeira execução
3. O administrador padrão é criado automaticamente:
   - **Utilizador:** admin
   - **Palavra-passe:** admin123

---

## Configuração opcional

### Número WhatsApp (variável de ambiente)

**Windows:**
```powershell
set WHATSAPP_NUMBER=258847749499
python app.py
```

**Linux/macOS:**
```bash
export WHATSAPP_NUMBER=258847749499
python app.py
```

---

## Resolução de problemas

**Erro "python não é reconhecido":**
- Use `python3` em vez de `python` (Linux/macOS)
- Certifique-se de que o Python está no PATH (Windows)

**Erro ao instalar dependências:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
