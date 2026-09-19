# Notas API com Docker

Este projeto é uma API pequena de anotações criada para demonstrar, na prática, como uma aplicação Python pode ser empacotada e executada com Docker.

A API salva cada anotação com seu texto e data/hora. O banco utilizado é o SQLite. Quando a aplicação roda no Docker, o banco fica em `/app/data/notas.db` e esse diretório é ligado ao volume nomeado `notas-dados`.

## O que foi praticado

- criação de uma imagem Docker própria;
- organização de um `Dockerfile` com aproveitamento de cache;
- execução de uma API Python dentro de um contêiner;
- uso de volume nomeado;
- comprovação de que os dados persistem mesmo após remover o contêiner;
- comparação com a execução sem volume, na qual os dados são perdidos.

## Tecnologias

- Python 3.12;
- FastAPI;
- Uvicorn;
- SQLite;
- Docker.

## Rotas disponíveis

| Método | Rota | Função |
|---|---|---|
| GET | `/health` | Verifica se a API está funcionando |
| POST | `/notas` | Cria uma anotação |
| GET | `/notas` | Lista as anotações salvas |
| GET | `/docs` | Abre a documentação interativa |

Para criar uma anotação, envie um JSON no formato:

```json
{"texto": "Minha primeira anotação"}
```

## Executar localmente

Na pasta do projeto, crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Depois acesse `http://localhost:8000/docs` ou teste pelo terminal:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/notas
```

## Executar com Docker

Construa a imagem:

```bash
docker build -t notas-api:1.0 .
```

Crie o volume nomeado:

```bash
docker volume create notas-dados
```

Inicie o contêiner:

```bash
docker run -d --name notas -p 8000:8000 -v notas-dados:/app/data notas-api:1.0
```

Confira se está funcionando:

```bash
docker ps
docker logs notas
curl http://localhost:8000/health
```

Crie uma anotação:

```bash
curl -X POST http://localhost:8000/notas \
  -H "Content-Type: application/json" \
  -d '{"texto":"Anotação criada no Docker"}'
```

Liste as anotações:

```bash
curl http://localhost:8000/notas
```

## Verificar a persistência

Remova o contêiner:

```bash
docker stop notas
docker rm notas
```

Crie outro contêiner usando o mesmo volume:

```bash
docker run -d --name notas2 -p 8000:8000 -v notas-dados:/app/data notas-api:1.0
```

As anotações anteriores deverão continuar disponíveis:

```bash
curl http://localhost:8000/notas
```

O relatório com as evidências e capturas está em [RELATORIO.md](RELATORIO.md).

## Limpeza

Para remover os contêineres de teste:

```bash
docker stop notas2 2>/dev/null || true
docker rm notas2 2>/dev/null || true
```

Para remover também o volume e apagar as anotações:

```bash
docker volume rm notas-dados
```

> A remoção do volume é definitiva para os dados armazenados nele.
