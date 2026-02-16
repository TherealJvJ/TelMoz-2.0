# Como Adicionar um Administrador com Gmail

## Método 1: Através do Painel Admin (Recomendado)

1. **Faça login** como administrador existente:
   - Acesse: `http://127.0.0.1:5000/admin/login`
   - Use as credenciais padrão: `admin` / `admin123`

2. **No Painel Admin**, clique em **"+ Novo Administrador"**

3. **Preencha o formulário**:
   - **Nome de Utilizador**: escolha um nome único (ex: `joao_silva`)
   - **Email**: use seu Gmail (ex: `joao.silva@gmail.com`)
   - **Senha**: mínimo 6 caracteres
   - **Confirmar Senha**: digite novamente

4. Clique em **"Criar Administrador"**

5. **Pronto!** O novo administrador pode fazer login usando:
   - **Utilizador**: o nome escolhido
   - **Senha**: a senha definida

---

## Método 2: Via Python (Linha de Comando)

Se preferir criar diretamente pelo terminal:

```python
# Execute no diretório do projeto
python
```

Depois execute:

```python
from app import app
from models import db, Admin

with app.app_context():
    # Criar novo admin
    novo_admin = Admin(
        username='joao_silva',
        email='joao.silva@gmail.com'
    )
    novo_admin.set_password('sua_senha_segura')
    
    db.session.add(novo_admin)
    db.session.commit()
    print('Administrador criado com sucesso!')
```

---

## Método 3: Script Python Separado

Crie um ficheiro `add_admin.py`:

```python
from app import app
from models import db, Admin

with app.app_context():
    username = input("Nome de utilizador: ")
    email = input("Email (Gmail): ")
    password = input("Senha: ")
    
    admin = Admin(username=username, email=email)
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    print(f'Administrador "{username}" criado!')
```

Execute:
```bash
python add_admin.py
```

---

## Recuperação de Senha

Se um administrador esquecer a senha:

1. Na página de login, clique em **"Esqueci a senha"**
2. Digite o **email** cadastrado
3. O sistema gerará um link de recuperação
4. **Em produção**, este link seria enviado por email
5. **Em desenvolvimento**, o link aparece na mensagem de sucesso
6. Acesse o link para redefinir a senha

**Nota**: O link expira em 1 hora.

---

## Exemplo Completo com Gmail

```python
from app import app
from models import db, Admin

with app.app_context():
    # Admin com Gmail
    admin_gmail = Admin(
        username='maria_santos',
        email='maria.santos@gmail.com'
    )
    admin_gmail.set_password('MinhaSenh@123')
    
    db.session.add(admin_gmail)
    db.session.commit()
    print('Admin criado: maria.santos@gmail.com')
```

---

## Dicas de Segurança

- Use senhas fortes (mínimo 6 caracteres, mas recomenda-se 8+)
- Combine letras, números e símbolos
- Não compartilhe credenciais
- Em produção, configure envio de email real para recuperação de senha
