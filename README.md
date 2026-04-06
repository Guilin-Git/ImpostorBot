# Documentação: Como criar, adicionar e rodar seu Bot do Discord

Siga este passo a passo para colocar o bot online no seu servidor e jogar com seus amigos!

---

## 🛠️ 1. Preparando o ambiente
1. Baixe e instale o [Python](https://www.python.org/downloads/).
   - **IMPORTANTE:** Durante a instalação no Windows, marque a caixa que diz **"Add Python to PATH"** na primeira tela.
2. Com o Python instalado, você precisa instalar a biblioteca responsável por conectar o bot ao Discord.
3. Abra o seu Terminal / Prompt de Comando e rode o seguinte comando:
   ```cmd
   pip install discord.py
   ```

---

## 🤖 2. Criando o Bot no Discord
1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications/).
2. Faça login com a sua conta do Discord.
3. Clique no botão azul **"New Application"** no canto superior direito.
4. Dê um nome para o seu bot (ex: Bot do Impostor) e concorde com os termos para criar.

---

## 🔑 3. Pegando o Token e Configurando as Permissões do Bot
1. No menu da esquerda, clique na aba **"Bot"**.
2. **IMPORTANTE - Habilitar INTENTS:** Role a página um pouco para baixo até achar a seção **"Privileged Gateway Intents"**. Você precisará **ATIVAR** as três opções para que o bot possa ver quem está no canal de voz e enviar mensagens:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
   *(Lembre-se de clicar em "Save Changes" depois de ativá-las).*
3. Role de volta para o topo da página do **"Bot"** e clique no botão **"Reset Token"**.
4. O Discord vai gerar uma chave misturada enorme. **COPIE ESSE TOKEN**. Guarde-o com você e não compartilhe com ninguém.
5. Abra o arquivo `bot.py` pelo bloco de notas (ou um editor de código como o VS Code) e encontre a linha no final:
   ```python
   TOKEN = 'COLOQUE_SEU_TOKEN_AQUI_DENTRO_DAS_ASPAS'
   ```
6. Substitua pelo token que você copiou:
   ```python
   TOKEN = 'MTAyOTM... (seu verdadeiro token aqui)'
   ```
   **Não se esqueça de salvar o arquivo `bot.py`!**

---

## 📲 4. Adicionando o Bot no seu Servidor
1. No menu esquerdo do Developer Portal, clique em **"OAuth2"** e depois **"URL Generator"**.
2. Na caixa "Scopes", marque a opção **"bot"**.
3. Irá abrir uma nova caixa "Bot Permissions". Marque as permissões:
   - `Send Messages`
   - `Read Messages/View Channels`
4. Copie o **Generated URL** (o link que aparecer na parte inferior da página).
5. Cole esse link no seu navegador. Ele vai perguntar em qual servidor você quer adicionar o bot. Autorize-o!

---

## ▶️ 5. Rodando o Bot
1. Abra o Terminal / Prompt de Comando.
2. Navegue até a pasta onde está o arquivo `bot.py`. (Exemplo: se você abriu no VS Code, apenas abra o terminal lá dentro, ou então use `cd c:\Users\PC\teste`).
3. Rode o comando para iniciar o bot:
   ```cmd
   python bot.py
   ```
4. Se der certo, aparecerá a mensagem no terminal:
   `🤖 Bot do Impostor (...) está online e pronto para jogar!`

---

## 🎮 6. Como Jogar
1. O bot deve estar constando como *Online* no seu servidor.
2. Entre em um **Canal de Voz** com seus amigos (vocês precisam de pelo menos 3 pessoas, sem contar o bot).
3. No chat de texto do servidor, digite:
   `!impostor`
4. O bot irá observar todos que estão no canal de voz naquele momento, e iniciará o jogo!
5. Cada pessoa receberá uma Mensagem Privada (DM). O impostor receberá a dica, e os inocentes receberão a palavra.

*(Aviso: É importante que os jogadores permitam Mensagens Diretas de membros do servidor nas configurações de privacidade do Discord, caso contrário o bot não conseguirá entregar a palavra/dica).*

Boa diversão! Cuidado com o impostor! 🤫
