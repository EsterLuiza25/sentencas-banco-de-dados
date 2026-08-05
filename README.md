# Coleta e Migração de Sentenças de Banco de Dados
---
Projeto em Python desenvolvido para raspagem, estruturação e migração de dados de sentenças judiciais para um banco de dados PostgreSQL.
---
## Descrição
---
O sistema realiza a extração automatizada de sentenças, faz o tratamento do conteúdo textual bruto (HTML e texto sem formatação), extrai metadados como datas relevantes e deduplica os processos. Os dados coletados são salvos em um banco relacional PostgreSQL para consulta e análise.

## Tecnologias Utilizadas
---
* Python 3.12+
* Poetry (Gerenciamento de dependências e ambientes virtuais)
* PostgreSQL (Banco de dados relacional)
* psycopg2-binary (Driver de conexão PostgreSQL)
* BeautifulSoup4 (Processamento de dados HTML)
* Requests (Requisições HTTP)
* SQLite (Armazenamento temporário local)
---
## Estrutura do Projeto

```text
sentencas-banco-de-dados/
├── .venv/                      # Ambiente virtual gerenciado pelo Poetry
├── client.py                   # Módulo de requisições à API/servidor
├── conexao.py                  # Script de teste de conexão com o PostgreSQL
├── db.py                       # Gerenciamento de tabelas e operações de banco
├── main.py                     # Script principal de execução da coleta
├── migracao_banco_postgres.py  # Script de migração de dados (SQLite para Postgres)
├── parser.py                   # Extração e tratamento de texto/datas
├── poetry.lock                 # Trava de versões das dependências
├── pyproject.toml              # Configuração do projeto e dependências Poetry
├── README.md                   # Documentação do projeto
└── requirements.txt            # Lista de dependências legada
