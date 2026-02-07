# Telmoz - Catálogo de Produtos

Site de catálogo de produtos para a empresa Telmoz, com redirecionamento para WhatsApp para efetuar compras.

## Funcionalidades

- **Público**: Visualizar produtos por categoria, clicar para comprar via WhatsApp (sem login)
- **Admin**: Login para adicionar/editar categorias e produtos
- **Cores**: Branco, verde e rosa bebê

## Instalação

1. Criar ambiente virtual (recomendado):
```bash
python -m venv venv
venv\Scripts\activate
```

2. Instalar dependências:
```bash
pip install -r requirements.txt
```

3. Executar a aplicação:
```bash
python app.py
```

4. Aceder em: http://127.0.0.1:5000

## Credenciais Admin (padrão)

- **Utilizador**: admin
- **Palavra-passe**: admin123

⚠️ Altere a palavra-passe em produção!

## Configuração WhatsApp

Edite no `app.py` a variável `WHATSAPP_NUMBER` com o número da empresa (formato: 5511999999999, com código do país).

Ou defina a variável de ambiente:
```bash
set WHATSAPP_NUMBER=5511999999999
```

## Estrutura do Projeto

```
Telmoz 2.0/
├── app.py              # Aplicação Flask
├── models.py           # Modelos da base de dados
├── requirements.txt
├── templates/          # Templates HTML
├── static/css/        # Estilos CSS
└── instance/          # Base de dados SQLite (criada automaticamente)
```
