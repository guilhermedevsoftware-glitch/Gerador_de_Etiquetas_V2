# Gerador de Etiquetas (MVP)

Sistema web para cadastro de produtos, geração de códigos de barras, QR Codes e
etiquetas em PDF, com histórico de impressões e controle de usuários.

## 1. O que é o projeto

Uma aplicação web feita com **Flask** que permite:

- Login de usuários (com perfis Administrador/Usuário);
- Cadastro completo de produtos (CRUD);
- Geração de código de barras (Code128 e EAN13) e QR Code por produto;
- Escolha entre 3 modelos de etiqueta pré-configurados;
- Montagem de uma lista de produtos + quantidades e geração de um PDF com
  todas as etiquetas;
- Pré-visualização da etiqueta antes de gerar o PDF;
- Histórico de todas as etiquetas geradas, com filtros e reimpressão do PDF;
- Gerenciamento de usuários (somente administradores).

## 2. Tecnologias utilizadas

- Python 3.10+
- Flask
- Flask-SQLAlchemy (SQLite)
- Flask-Login
- Werkzeug (hash de senha)
- ReportLab (geração de PDF)
- python-barcode (código de barras)
- qrcode + Pillow (QR Code)
- Bootstrap 5 + Bootstrap Icons (interface)

## 3. Como instalar o Python

Baixe e instale o Python 3.10 ou superior em https://www.python.org/downloads/.
Durante a instalação no Windows, marque a opção **"Add Python to PATH"**.

Para verificar se foi instalado corretamente:

```bash
python --version
```

## 4. Como criar o ambiente virtual

Dentro da pasta do projeto (`gerador_etiquetas`), execute:

```bash
python -m venv venv
```

Ativar o ambiente virtual:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

Você saberá que o ambiente está ativo quando `(venv)` aparecer no início da
linha do terminal.

## 5. Como instalar as dependências

Com o ambiente virtual ativado, execute:

```bash
pip install -r requirements.txt
```

## 6. Como executar o projeto

```bash
python app.py
```

O sistema criará automaticamente o arquivo `database.db` (SQLite) na primeira
execução, já populado com um usuário administrador, os 3 modelos de etiqueta
e 5 produtos de exemplo.

Depois de iniciar, acesse no navegador:

```
http://localhost:5000
```

## 7. Usuário inicial

```
E-mail: admin@admin.com
Senha:  Admin@123
```

> A senha é armazenada com hash seguro (Werkzeug) — nunca em texto puro.

## 8. Como utilizar o sistema

1. Faça login com o usuário administrador acima;
2. Em **Produtos**, cadastre, edite ou consulte os produtos (já existem 5
   produtos de exemplo prontos para teste);
3. Em **Modelos**, veja os 3 modelos de etiqueta pré-configurados (Simples,
   com Código de Barras e com QR Code). Um administrador pode ajustar nome,
   dimensões e status de cada modelo;
4. Em **Gerar Etiquetas**:
   - Pesquise um produto pelo nome ou código;
   - Informe a quantidade e clique em **Adicionar**;
   - Repita para outros produtos, se necessário;
   - Escolha o modelo de etiqueta desejado;
   - Clique em **Visualizar** para ver uma prévia da etiqueta;
   - Clique em **Gerar PDF** para montar o arquivo com todas as etiquetas
     solicitadas (o PDF abre diretamente no navegador);
5. Em **Histórico**, consulte todas as etiquetas já geradas, filtre por data,
   usuário ou modelo, veja os detalhes de cada impressão e gere o PDF
   novamente quando precisar;
6. Em **Usuários** (apenas administradores), cadastre novos usuários,
   defina o perfil (Administrador/Usuário) e ative/desative contas.

## 9. Estrutura das pastas

```text
gerador_etiquetas/
│
├── app.py                  # Ponto de entrada da aplicação (cria o app e o banco)
├── extensions.py           # Instâncias compartilhadas (SQLAlchemy, LoginManager)
├── requirements.txt
├── database.db             # Criado automaticamente na primeira execução
│
├── models/                 # Modelos SQLAlchemy (tabelas do banco)
│   ├── usuario.py
│   ├── produto.py
│   ├── modelo_etiqueta.py
│   └── impressao.py
│
├── routes/                 # Blueprints (rotas/controladores)
│   ├── auth.py
│   ├── dashboard.py
│   ├── produtos.py
│   ├── etiquetas.py
│   ├── modelos.py
│   ├── usuarios.py
│   └── historico.py
│
├── services/                # Regras de negócio isoladas
│   ├── barcode_service.py   # Geração de código de barras
│   ├── qrcode_service.py    # Geração de QR Code
│   └── pdf_service.py       # Montagem do PDF de etiquetas
│
├── templates/                # Views HTML (Jinja2)
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── erro.html
│   ├── partials/
│   ├── produtos/
│   ├── etiquetas/
│   ├── modelos/
│   ├── usuarios/
│   └── historico/
│
└── static/
    ├── css/style.css
    ├── js/app.js
    └── generated/             # Códigos de barras, QR Codes e PDFs gerados
```

## 10. Observações

- Este é um MVP: os 3 modelos de etiqueta são pré-configurados (sem editor
  visual drag-and-drop), conforme escopo definido para esta primeira versão;
- Os arquivos gerados (imagens de código de barras/QR Code e PDFs) ficam em
  `static/generated/` e podem ser apagados a qualquer momento sem afetar o
  funcionamento do sistema — eles são recriados automaticamente quando
  necessário (inclusive ao reimprimir um PDF do histórico).
