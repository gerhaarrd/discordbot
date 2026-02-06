# 🤖 Discord Bot

Bot para Discord desenvolvido em **Python**, utilizando **discord.py**.
Projeto focado em componentes de interface (`LayoutView`, containers, seções e displays customizados), permitindo criar mensagens mais modernas e organizadas dentro do Discord.

---

## 📌 Funcionalidades

* Interface customizada usando **Discord UI Components**
* Sistema baseado em **Views e Containers**
* Estrutura simples para expansão
* Uso de `.env` para segurança do token
* Base para criação de comandos e interações

---

## 🛠️ Tecnologias utilizadas

* Python 3.x
* discord.py
* python-dotenv
* Virtualenv (recomendado)

---

## 📂 Estrutura do projeto

```
discordbot/
│
├── bot.py              # Arquivo principal do bot
├── requirements.txt    # Dependências do projeto
├── .env.example        # Exemplo de variáveis de ambiente
└── README.md
```

---

## ⚙️ Instalação

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/gerhaarrd/discordbot.git
cd discordbot
```

---

### 2️⃣ Criar ambiente virtual (recomendado)

#### Linux / Mac

```bash
python -m venv .venv
source .venv/bin/activate
```

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

### 3️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Agora edite o `.env` e adicione o token do bot:

```
TOKEN=seu_token_aqui
GUILD_ID=id_do_server
```

---

## ▶️ Executar o bot

```bash
python bot.py
```

Se tudo estiver correto, o bot ficará online.

---

## 🔑 Como criar um bot no Discord

1. Acesse o Discord Developer Portal
   👉 [https://discord.com/developers/applications](https://discord.com/developers/applications)

2. Crie uma nova aplicação

3. Vá em **Bot → Add Bot**

4. Copie o token e coloque no `.env`

5. Configure as permissões e convide o bot para o servidor

---

## 🧩 Expansão do projeto

Você pode adicionar:

* Slash commands
* Sistema de permissões
* Banco de dados
* Logs
* Integrações com APIs
* Sistemas interativos com botões e menus

---

## ⚠️ Segurança

❌ Nunca compartilhe seu token
❌ Nunca suba o `.env` para o GitHub
✔ Use `.env.example` para mostrar a estrutura

---

## 📜 Licença

Este projeto é open-source e pode ser utilizado para estudos e projetos pessoais.

---

## 👤 Autor

Desenvolvido por **Gerhard**
🔗 [https://github.com/gerhaarrd](https://github.com/gerhaarrd)
