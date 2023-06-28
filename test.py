import requests

# URL del endpoint "/sensor" de la API
url = 'http://127.0.0.1:8000/sensor'

# Datos de prueba
data = {'temperature': 25.5}

# Enviar la solicitud POST con los datos de prueba
response = requests.post(url, json=data)

# Imprimir la respuesta
print(response.text)
