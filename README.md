# 📈 Telegram Market Report Bot (Hybrid Mode)

Este projeto consiste em um bot interativo para Telegram que monitora ativos financeiros (Ações e Criptomoedas). Ele foi reestruturado para um **modelo híbrido de execução**, otimizando o consumo de memória RAM em servidores limitados (ex: instâncias de 1GB).

## Arquitetura do Projeto

O projeto é dividido em dois componentes principais para economizar recursos:

1. **Listener (Bot de Escuta):** Um script leve que roda 24/7, consumindo o mínimo de RAM (~20MB), apenas aguardando comandos no Telegram.
    
2. **Worker (Processador):** Um script robusto que carrega as bibliotecas financeiras (`yfinance`, `pandas`), processa os dados e envia o relatório. Ele é executado apenas sob demanda e encerra logo após o envio, liberando memória para o sistema.
    

## Funcionalidades

- **Baixo Consumo:** Ideal para rodar junto com servidores Web (Apache/Nginx) e outros scripts.
    
- **Relatório sob Demanda:** Digite `/relatorio` no bot e receba os dados atualizados em segundos.
    
- **Agendamento via Cron:** O Worker pode ser chamado pelo Cron do sistema para relatórios automáticos.
    
- **Análise de Tendência:** Compara o preço atual com a Média Móvel (SMA 20) e identifica máximas/mínimas de 7 dias.
    

## Instalação e Configuração

### 1. Requisitos

- Python 3.10+
    
- Token de Bot do Telegram (obtido via @BotFather)

## Como Instalar

### 1. Clonar o repositório
```bash
git clone [https://github.com/rubenslpdev/market-report.git](https://github.com/rubenslpdev/market-report.git)
cd market-report


### 2. Configurar o ambiente virtual e dependências


python3 -m venv venv
source venv/bin/activate
pip install python-telegram-bot yfinance python-dotenv requests
```

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

Code snippet

```
TELEGRAM_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

### 4. Configurar Ativos

Edite o arquivo `config.json` para adicionar seus ativos:

```json
{
  "ativos": {
    "stocks": [
      { "ticker": "PETR4.SA" },
      { "ticker": "VALE3.SA" }
    ],
    "criptos": [
      { "ticker": "BTC-USD" },
      { "ticker": "ETH-USD" }
    ]
  }
}
```

## 🤖 Execução e Persistência (Linux)

Para garantir que o bot rode 24/7 e inicie automaticamente com o servidor, utilize o **Systemd**.

1. Crie o arquivo de serviço:
    
    ```bash
    sudo nano /etc/systemd/system/marketreport.service
    ```
    
2. Adicione o conteúdo abaixo (ajustando os caminhos):

```TOML
    [Unit]
    Description=Bot de Relatorio Financeiro
    After=network.target
    
    [Service]
    Type=simple
    User=ubuntu
    WorkingDirectory=/home/ubuntu/Projetos/python/marketreport
	ExecStart=/home/ubuntu/Projetos/python/marketreport/.venv/bin/python3 /home/ubuntu/Projetos/python/marketreport/market_listener.py
    Restart=always
    
    [Install]
    WantedBy=multi-user.target
```

3. Ative o serviço:
    
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable marketreport
    sudo systemctl start marketreport
    ```
    

### No Cron (Relatório Automático)

Para manter o relatório semanal toda segunda às 08:00 sem precisar do bot acordado para isso, adicione no seu `crontab -e`:

```bash
0 8 * * 1 /home/ubuntu/Projetos/python/marketreport/.venv/bin/python3 /home/ubuntu/Projetos/python/marketreport/market_reporter.py
```

---

## 📊 Comandos Disponíveis

- `/start`: Mensagem de boas-vindas.
    
- `/relatorio`: Gera e envia o relatório financeiro atualizado.
    

---
## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](https://www.google.com/search?q=LICENSE&authuser=1) para detalhes.

---

