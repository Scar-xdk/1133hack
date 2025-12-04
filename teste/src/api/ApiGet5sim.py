import requests

# -------- CONFIGURAÇÃO --------
BASE_URL_V1 = "https://5sim.net/v1"
API_TOKEN = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODI1MjQ2NzksImlhdCI6MTc1MDk4ODY3OSwicmF5IjoiN2EyYzUzMWViMDFlZjdmYWVkNjRmMTMxZDAyMmIzNWYiLCJzdWIiOjMyNzMxNzd9.rUX7pOdG1JLGdp3nY2f48XSS5-0WRCPGqM53WMkiPQEaeR4bNie8Vwu3FrlkoysR8ik9YFGiaq6RYkjqsI4HHQH5A5t69YAFQfGMyXl_FY_-NqHcMvyvW-nvwwTRkk644HuzvIt_QUJmZr8vf0BwZlJ1mbDPsC--h2DiQKlz0Ngiqma5IS1n_qThE-R4L9oXx7CFONtsbDhxlqPIXMzWYLkhQAQaWZVG6BxHVC25B9ecXQtUNAjIpvG-N6YFR9uE6IyTijrCe-2CAUQ-fEH4bHNqqx_bZIyrd9vZBqbhbVwYdD-k7qe3pKDxj03yKRws98zAq0efJ9i8JyXiNjwvfQ"

HEADERS_V1 = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

# -------- FUNÇÕES NOVA API (v1) --------

def pedir_numero(product, country):
    url = f"{BASE_URL_V1}/user/buy/number/{product}/{country}"
    r = requests.get(url, headers=HEADERS_V1)
    return r.json()

def checar_status(order_id):
    url = f"{BASE_URL_V1}/user/check/{order_id}"
    r = requests.get(url, headers=HEADERS_V1)
    return r.json()

def buscar_servicos_por_pais(country):
    url = f"https://5sim.net/v1/guest/products/{country}/any"
    r = requests.get(url)

    try:
        return r.json()
    except:
        return {}


def ativacoes_anteriores():
    url = f"{BASE_URL_V1}/user/activation/history"
    r = requests.get(url, headers=HEADERS_V1)
    return r.json()

def reativar_numero(product, number):
    url = f"{BASE_URL_V1}/user/reuse/{product}/{number}"
    r = requests.get(url, headers=HEADERS_V1)
    return r.json()

# -------- FUNÇÕES ANTIGA API (API1) --------

BASE_URL_API1 = "http://api1.5sim.net/stubs/handler_api.php"
API_KEY_OLD = "SUA_API_KEY_OLD"

def ver_balance_api1():
    url = f"{BASE_URL_API1}?action=getBalance&api_key={API_KEY_OLD}"
    return requests.get(url).text

def pedir_numero_api1(product, country):
    url = f"{BASE_URL_API1}?api_key={API_KEY_OLD}&action=getNumber&service={product}&country={country}"
    return requests.get(url).text

def checar_status_api1(order_id):
    url = f"{BASE_URL_API1}?api_key={API_KEY_OLD}&action=getStatus&id={order_id}"
    return requests.get(url).text
