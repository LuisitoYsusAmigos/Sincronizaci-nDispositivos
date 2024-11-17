import requests

# Definir el ID del dispositivo
id_dispositivo = 4

# Configurar la URL y el JSON de la solicitud
url = "http://127.0.0.1:5000/encendidoPlaca"
payload = {
    "id_dispositivo": id_dispositivo
}

# Realizar la solicitud POST y capturar la respuesta
response = requests.post(url, json=payload)

# Imprimir la respuesta de la API
print("Respuesta de la API:", response.json())
