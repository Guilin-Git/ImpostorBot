# Guia de Comandos do Bot de Impostor

Aqui está a lista unificada de todos os comandos que você e seus amigos podem usar:

### 🎮 Comandos de Jogo
- **`!impostor`**
  - **O que faz:** Modo clássico. Inicia uma partida pegando todos que estão no canal de voz, escolhendo o Impostor aleatoriamente e tirando palpites de fábrica do arquivo `palavras.json`.

- **`!impostor [tema]`**
  - **Exemplo:** `!impostor filmes de terror`
  - **O que faz:** Modo Inteligência Artificial. Em vez de usar palavras prontas do bot, ele comunica velozmente via rede local com o Ollama (`gemma3:4b`), dizendo a ele o tema específico que você definiu. A IA vai na hora pensar numa palavra criativa desse universo e bolar a pista vaga separada para a partida.

- **`!stop_game`**
  - **O que faz:** Força o fechamento da partida. Foi bater um vento forte e os amigos tiveram que desconectar no meio do turno? Digite isso. O bot imediatamente cancela tudo o que estaja esperando e libera o servidor de travas de loop pra poder inicializar outro.

### ⚙️ Comandos de Configuração
- **`!set_time <segundos>`**
  - **Exemplo:** `!set_time 15`
  - **O que faz:** Define para 15 segundos o tempo máximo que um jogador terá quando chegar a vez dele para digitar uma palavra no chat.

- **`!set_turns <rodadas>`**
  - **Exemplo:** `!set_turns 4`
  - **O que faz:** Define a quantidade de ciclos na mesma pessoa. A partida inteira passa por cada jogador 4 vezes até abrir a etapa da votação final.

### 🏆 Comando de Placar Global
- **`!leaderboard`**
  - **O que faz:** Exibe a tabela de classificações de todo o servidor embutida no chat! Se um impostor enganar as pessoas, ele leva 1 ponto pro bolso. Se as pessoas pegarem ele atirando no buraco da votação, TODOS os inocentes da partida levam 1 ponto. Ele mostra os 10 mais viciados nessa listinha.
