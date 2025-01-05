# Projeto de Ingestão de Repositórios do GitHub

## Objetivos
Este projeto tem como objetivo realizar a ingestão de dados de repositórios do GitHub e armazená-los no Azure Blob Storage. Ele utiliza Azure Functions para automatizar e gerenciar o processo de ingestão.

## O que ela faz
O projeto baixa arquivos de repositórios do GitHub e os armazena no Azure Blob Storage. Ele pode realizar a ingestão completa de diretórios específicos ou a ingestão incremental de arquivos atualizados nos últimos dias.

## Funções

### DailyIngestion
- **Trigger**: Timer Trigger
- **Descrição**: Executa a ingestão incremental de arquivos atualizados nos últimos dias a partir de um repositório do GitHub.
- **Arquivo**: [DailyIngestion/__init__.py](DailyIngestion/__init__.py)

### HTTPCreateCrawlerJobs
- **Trigger**: HTTP Trigger
- **Descrição**: Cria mensagens na fila do Azure Storage Queue para a ingestão de diretórios específicos do repositório do GitHub.
- **Arquivo**: [HTTPCreateCrawlerJobs/__init__.py](HTTPCreateCrawlerJobs/__init__.py)

### HTTPSync
- **Trigger**: HTTP Trigger
- **Descrição**: Executa a ingestão completa de diretórios específicos do repositório do GitHub.
- **Arquivo**: [HTTPSync/__init__.py](HTTPSync/__init__.py)

### QueueJobsSync
- **Trigger**: Queue Trigger
- **Descrição**: Processa mensagens da fila do Azure Storage Queue e executa a ingestão completa dos diretórios especificados.
- **Arquivo**: [QueueJobsSync/__init__.py](QueueJobsSync/__init__.py)

### TimerCreateCrawlerJobs
- **Trigger**: Timer Trigger
- **Descrição**: Cria mensagens na fila do Azure Storage Queue para a ingestão de diretórios específicos do repositório do GitHub em intervalos regulares.
- **Arquivo**: [TimerCreateCrawlerJobs/__init__.py](TimerCreateCrawlerJobs/__init__.py)