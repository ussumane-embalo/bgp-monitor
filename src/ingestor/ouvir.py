import json
import time
from pathlib import Path                                       # NOVO
import websocket
import yaml                                                    # NOVO
import requests
URL = "wss://ris-live.ripe.net/v1/ws/?client=bgp-monitor-estudo"
CONFIG = Path(__file__).resolve().parents[2] / "config" / "vizinhos.yaml"   # NOVO
VERBOSO = True

def carregar_declarados():                                     # NOVO
    with open(CONFIG, encoding="utf-8") as f:                  # NOVO
        dados = yaml.safe_load(f)                              # NOVO
    return {int(asn): set(vizinhos) for asn, vizinhos in dados.items()}   # NOVO


def validar_rpki(origem, prefixo):
    url = f"http://localhost:9556/api/v1/validity/AS{origem}/{prefixo}"
    try:
        resposta = requests.get(url, timeout=5).json()
        return resposta["validated_route"]["validity"]["state"]
    except requests.RequestException:
        return None

DECLARADOS = carregar_declarados()                             # MUDOU: já não está escrito à mão
print("Lista declarada carregada:", DECLARADOS)                # NOVO

def ligar():
    ws = websocket.WebSocket()
    ws.connect(URL)
    ws.send(json.dumps({
        "type": "ris_subscribe",
        "data": {"path": 6939}
    }))
    print("Ligado. À espera de anúncios...")
    return ws

while True:
    try:
        ws = ligar()
        while True:
            msg = json.loads(ws.recv())
            if msg["type"] != "ris_message":
                print("MENSAGEM DO SERVIDOR:", msg)
                continue
            dados = msg["data"]
            if dados.get("type") != "UPDATE":
                continue
            caminho = dados.get("path", [])
            for anuncio in dados.get("announcements", []):
                for prefixo in anuncio["prefixes"]:
                    origem = caminho[-1]
                    vizinho = caminho[-2] if len(caminho) >= 2 else None
                    if isinstance(origem, list) or isinstance(vizinho, list):
                        continue
                    estado = validar_rpki(64511, prefixo) if origem in DECLARADOS else None
                    if estado == "invalid":
                        print("ALERTA RPKI inválido:", prefixo, "origem", origem)
                    elif VERBOSO and estado:
                        print("rpki:", estado, prefixo)

                    if origem in DECLARADOS and vizinho not in DECLARADOS[origem]:
                        print("ALERTA vizinho inesperado:", prefixo, caminho)
                    elif VERBOSO and origem in DECLARADOS:
                        print("ok:", prefixo, "| vizinho", vizinho, "declarado")
    except (websocket.WebSocketException, OSError) as erro:
        print("Ligação perdida:", erro)
        print("A voltar a ligar em 5 segundos...")
        time.sleep(5)