#  Market Report - Relatório de Ativos

Um script em Python simples e eficiente que extrai dados financeiros (Ações da B3 e Criptomoedas), analisa tendências baseadas em Média Móvel Simples (SMA 20) e envia um relatório automatizado diretamente para o seu Telegram.

##  Funcionalidades

- **Cotação em Tempo Real (fechamento):** Busca o último preço disponível dos ativos configurados.
- **Análise de Tendência (SMA 20):** Calcula a Média Móvel Simples de 20 períodos para definir se o ativo está em tendência de Alta 📈 ou Baixa 📉.
- **Mínimas e Máximas:** Retorna o menor e o maior preço negociado nos últimos 7 pregões/dias.
- **Suporte Multi-Ativos:** Funciona nativamente com ações da Bolsa Brasileira (B3), índices (ex: IBOV) e Criptomoedas globais.
- **Configuração via JSON:** Facilidade para adicionar ou remover ativos sem mexer no código Python.
- **Integração com Telegram:** Envio direto via API do Telegram (`requests`), formatado em HTML para melhor legibilidade no celular.

##  Tecnologias Utilizadas

- [Python 3.x](https://www.python.org/)
- [yfinance](https://pypi.org/project/yfinance/) - Obtenção dos dados financeiros do Yahoo Finance.
- [pandas](https://pandas.pydata.org/) - Manipulação de dados e cálculo da média móvel.
- [requests](https://pypi.org/project/requests/) - Comunicação com a API do Telegram.
- [python-dotenv](https://pypi.org/project/python-dotenv/) - Gerenciamento seguro de credenciais via arquivo `.env`.

##  Pré-requisitos e Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/rubenslpdev/python/marketreport.git
   cd marketreport 
   ```

2. **Instale as dependências:**
   ```bash
   pip install yfinance requests python-dotenv pandas
   ```

3. **Configuração do Bot do Telegram:**
   - Procure o `@BotFather` no Telegram e crie um novo bot para obter o **Token**.
   - Inicie uma conversa com seu novo bot.
   - Para descobrir o seu Chat ID, você pode enviar uma mensagem para o bot e acessar a URL: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`.

4. **Configuração das Variáveis de Ambiente:**
   - Crie um arquivo chamado `.env` na raiz do projeto e insira suas credenciais:
   ```env
   TELEGRAM_TOKEN=seu_token_aqui
   TELEGRAM_CHAT_ID=seu_chat_id_aqui
   ```

5. **Configuração dos Ativos:**
   - Edite o arquivo `config.json` com os ativos desejados. Lembre-se de usar o sufixo `.SA` para ações brasileiras:
   ```json
   {
     "ativos": {
       "stocks": [
         { "ticker": "PETR4.SA" },
         { "ticker": "^BVSP" }
       ],
       "criptos": [
         { "ticker": "BTC-USD" }
       ]
     }
   }
   ```

##  Como Usar

Com as configurações prontas, basta executar o script principal:

```bash
python bot_relatorio.py
```

Você receberá imediatamente uma mensagem no seu Telegram semelhante a esta:

> 📊 **Relatório Diário de Ativos**
>
> 🏢 **Ações (B3) e Índice**
> 🔸 **PETR4**: R$ 42.50 | Alta 📈
>    └ *Min 7d: R$ 40.10 / Max 7d: R$ 43.00*
> 🔸 **^BVSP**: R$ 130000.00 | Alta 📈
>    └ *Min 7d: R$ 128500.00 / Max 7d: R$ 131200.00*
>
> 🪙 **Criptomoedas**
> 🔸 **BTC-USD**: $ 65,000.00 | Baixa 📉
>    └ *Min 7d: $ 63,500.00 / Max 7d: $ 67,200.00*

##  Dica: Automação (Cron Job)
Para que o bot rode sozinho todos os dias (ex: após o fechamento do mercado), você pode configurar um *cron job* (Linux/Mac) ou o *Agendador de Tarefas* (Windows).

Exemplo de Cron Job para rodar de segunda a sexta às 18:30:
```bash
30 18 * * 1-5 /caminho/para/o/seu/python /caminho/para/o/bot_relatorio.py
```

##  Licença
Este projeto é de código aberto e está disponível sob a licença MIT. Sinta-se à vontade para clonar, modificar e utilizar!

