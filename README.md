# Coleta, Atualização Incremental e Migração de Sentenças

Pipeline de dados robusto desenvolvido em Python voltado para raspagem contínua, sanitização textual e ingestão incremental de sentenças judiciais em banco de dados relacional PostgreSQL. O sistema conta com mecanismo nativo de deduplicação e idempotência via chave única, estratégia de parada antecipada (early stopping) para otimização de requisições de rede e persistência em ambiente isolado via Docker Compose. Projetado para operação autônoma diária através do Agendador de Tarefas do Windows, assegurando integridade histórica, monitoramento via logs estruturados e alta performance no tratamento de jurisprudência criminal e militar.

---

## 1. Visão Geral da Arquitetura

O sistema atua como uma esteira contínua de extração e monitoramento de jurisprudência militar. O pipeline realiza varreduras parametrizadas sobre um catálogo de 30 termos jurídicos distintos, identificando decisões recentes disponibilizadas pelo tribunal, tratando o texto bruto e aplicando regras de deduplicação antes da gravação no banco de dados.

```text
[ Fonte Externa / Tribunal ]
              │
              ▼ (Pedidos HTTP Paginados)
     [ src/infra/http/client.py ] 
              │
              ▼ (Markup HTML Bruto)
    [ src/infra/parsers/parser.py ] ───► Sanitização, Regex de Datas e Extração
              │
              ▼ (Estruturas Normalizadas)
  [ src/presentation/main.py ] ────────► Orquestração do Fluxo e Paragem Antecipada
              │
              ▼ (Upsert Idempotente na Porta 5432)
   [ src/infra/database/db.py ] ───────► Conexão via psycopg2
              │
              ▼
       [ PostgreSQL 15 ] ──────────────► Chave Única + Volume Docker Persistente
```


## Funcionalidades Principais

* **Sincronização Diária Incremental:** Identifica novos processos publicados e atualiza automaticamente decisões existentes com novas juntadas ou alterações de conteúdo.
* **Cobertura Temática Expandida:** Monitoramento contínuo de 30 crimes e termos militares jurídicos.
* **Tratamento e Extração de Metadados:** Parsing de texto bruto, sanitização em HTML, cálculo de hash de integridade e extração regex de datas relevantes.
* **Persistência Confiável:** Armazenamento relacional estruturado no PostgreSQL com prevenção de duplicatas via `UNIQUE` constraints e upserts idempotentes.
* **Ambiente Conteinerizado:** Orquestração completa de banco e aplicação via Docker e Docker Compose com verificações de integridade (`healthcheck`).
* **Automação em Segundo Plano:** Suporte a agendamento automático diário via Task Scheduler (Windows) / rotinas cron.

---

## Tecnologias Utilizadas

* **Python 3.14+**
* **Poetry** (Gerenciamento de dependências e ambiente)
* **PostgreSQL 15+** (Banco de dados relacional)
* **Docker & Docker Compose** (Conteinerização e orquestração)
* **psycopg2-binary** (Driver de conexão com PostgreSQL)
* **Re e HTML** (Sanitização e processamento de HTML)
* **Requests** (Comunicação HTTP e integração com a API)

---

## Estrutura do Projeto

```text
sentencas-banco-de-dados/
├── src/
│   ├── application/               # Casos de uso e orquestração de fluxos (preparado para expansão)
│   ├── domain/                    # Entidades de negócio e contratos de repositório
│   ├── infra/                     # Implementações técnicas e integrações externas
│   │   ├── database/
│   │   │   ├── conexao.py         # Gestão de pool e ligação à base de dados
│   │   │   └── db.py              # DDL e operações de persistência/upsert
│   │   ├── http/
│   │   │   └── client.py          # Cliente HTTP para consumo de fontes externas
│   │   ├── parsers/
│   │   │   └── parser.py          # Sanitização de texto, hashes e regex de datas
│   │   └── scripts/
│   │       └── migraca_banco_postgres.py # Utilitários de migração
│   └── presentation/              # Pontos de entrada da aplicação
│       └── main.py                # Executável de orquestração do pipeline de coleta
│
├── tests/                         # Testes automatizados
├── .dockerignore                  # Ficheiros excluídos da imagem Docker
├── .env                           # Definições de ambiente locais (não versionado)
├── .gitignore                     # Ficheiros ignorados pelo controlo de versões
├── docker-compose.yml             # Orquestração do serviço PostgreSQL e rede
├── Dockerfile                     # Construção do contentor da aplicação
├── executar_coleta.bat            # Script de disparo para o Agendador de Tarefas
├── logs_execucao.txt              # Saída estruturada das execuções periódicas
├── poetry.lock                    # Ficheiro de bloqueio de versões exatas
├── pyproject.toml                 # Metadados e dependências do projeto
├── README.md                      # Documentação técnica do repositório
└── requirements.txt               # Export de dependências legadas
```

---
 
## Referências e Documentação Utilizada
 
A concepção da arquitetura, padrões de resiliência e implementação técnica se basearam nas seguintes documentações e padrões oficiais:
 
### Linguagem e Ecossistema Python
* [Python 3 Documentation](https://docs.python.org/3/) - Referência oficial da linguagem, manipulação de arquivos com `pathlib` e subprocessos.
* [Poetry Documentation](https://python-poetry.org/docs/) - Padrões de empacotamento, isolamento de ambientes virtuais e resolução determinística de dependências via lockfiles.
* [psycopg2 Documentation](https://www.psycopg.org/docs/) - Driver PostgreSQL para Python, gerenciamento de transações, cursores e execução parametrizada segura.
* [python-dotenv Documentation](https://github.com/theskumar/python-dotenv) - Boas práticas para carregamento e isolamento de variáveis de ambiente baseadas na metodologia The Twelve-Factor App.
 
### Banco de Dados e Persistência
* [PostgreSQL 15 Documentation](https://www.postgresql.org/docs/15/) - Modelagem de dados, restrições de integridade (`UNIQUE`), índices e sintaxe de upsert via cláusula `ON CONFLICT DO UPDATE`.
* [PostgreSQL Window Functions](https://www.postgresql.org/docs/15/tutorial-window.html) - Utilização de `ROW_NUMBER()` e particionamento para análise e auditoria de distribuição de termos.
 
### Infraestrutura e Automação
* [Docker Documentation](https://docs.docker.com/) - Construção de imagens com Dockerfile, boas práticas de camadas e imagens Alpine.
* [Docker Compose Specification](https://docs.docker.com/compose/) - Orquestração de múltiplos serviços, configuração de redes internas tipo bridge, volumes persistentes e monitoramento de dependência com `healthcheck`.
* [Microsoft Learn: Agendador de Tarefas do Windows](https://learn.microsoft.com/pt-br/windows/win32/taskschd/task-scheduler-start-page) - Configuração de tarefas agendadas, scripts `.bat` e redirecionamento de fluxos de saída/erros (`stdout`/`stderr`) para arquivos de log.
