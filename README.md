# Coleta, Atualização Incremental e Migração de Sentenças

Pipeline de dados robusto desenvolvido em Python voltado para raspagem contínua, sanitização textual e ingestão incremental de sentenças judiciais em banco de dados relacional PostgreSQL. O sistema conta com mecanismo nativo de deduplicação e idempotência via chave única, estratégia de parada antecipada (early stopping) para otimização de requisições de rede e persistência em ambiente isolado via Docker Compose. Projetado para operação autônoma diária através do Agendador de Tarefas do Windows, assegurando integridade histórica, monitoramento via logs estruturados e alta performance no tratamento de jurisprudência criminal e militar.

---

## 1. Visão Geral da Arquitetura

O sistema atua como uma esteira contínua de extração e monitoramento de jurisprudência militar. O pipeline realiza varreduras parametrizadas sobre um catálogo de 30 termos jurídicos distintos, identificando decisões recentes disponibilizadas pelo tribunal, tratando o texto bruto e aplicando regras de deduplicação antes da gravação no banco de dados.

```text
[ Fonte Externa / Tribunal ]
              │
              ▼ (Requisições HTTP Paginadas)
     [ client.py ] 
              │
              ▼ (Markup HTML Bruto)
     [ parser.py ] ───► Sanitização, Regex de Datas e Extração Estruturada
              │
              ▼ (Dicionários Normalizados)
       [ main.py ] ───► Controle de Fluxo e Parada Antecipada (Janela de 3 Páginas)
              │
              ▼ (Upsert Idempotente na Porta 5432)
   [ PostgreSQL 15 ] ───► Chave Única (numero_processo) + Volume Docker Persistente
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
├── .dockerignore              # Arquivos excluídos da imagem Docker
├── .gitignore                 # Arquivos ignorados pelo Git
├── docker-compose.yml         # Orquestração dos serviços (App + PostgreSQL)
├── Dockerfile                 # Definição do container da aplicação
├── client.py                  # Integração e consumo da API do tribunal
├── db.py                      # Camada de banco: tabelas, conexões e upserts
├── main.py                    # Pipeline de execução e controle incremental
├── parser.py                  # Sanitização textual, hash e extração de datas
├── poetry.lock                # Trava de versões exatas das dependências
├── pyproject.toml             # Configurações do projeto e dependências Poetry
├── README.md                  # Documentação do projeto
└── requirements.txt           # Export de dependências
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
