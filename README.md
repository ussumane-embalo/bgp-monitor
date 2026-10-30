# bgp-monitor

Monitor open source de segurança BGP. Ouve anúncios BGP públicos em tempo real e deteta anomalias: hijacks de origem, sub-prefixos e vizinhos inesperados junto à origem.

## Estado

Em desenvolvimento.

- Feito: ingestor em Python com RIS Live, validação RPKI via Routinator, lista declarada de vizinhos em YAML, reconexão automática.
- Planeado: alerta de sub-prefixo, deteção de route leak, métricas e dashboards, laboratório com ataques simulados.

## Como funciona

1. Liga-se ao RIPE RIS Live e recebe anúncios BGP.
2. Lê a origem e o vizinho da origem no AS path.
3. Pergunta ao Routinator se a origem pode anunciar o prefixo (valid, invalid, not-found).
4. Compara o vizinho da origem com a lista declarada em `config/vizinhos.yaml`.

## Como correr

Requisitos: Python 3 e Docker.

```
docker run -d --name routinator -p 3323:3323 -p 9556:9556 nlnetlabs/routinator
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src\ingestor\ouvir.py
```

Na primeira vez, o Routinator demora cerca de 30 minutos a descarregar os dados RPKI.

## Configuração

`config/vizinhos.yaml` lista, por AS de origem, os vizinhos legítimos. O exemplo incluído é só de demonstração e não foi validado pelo dono do AS.

## Aviso

A ferramenta só lê dados públicos e emite alertas. Não altera rotas nem envia anúncios.