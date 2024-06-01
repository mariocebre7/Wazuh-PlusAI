#!/var/ossec/framework/python/bin/python3
import os
import json
import time
import sys
from socket import socket, AF_UNIX, SOCK_DGRAM

try:
    import requests
    from requests.auth import HTTPBasicAuth
except Exception as e:
    print("Modulo 'requests' no encontrado. Para instalar: pip install requests")
    sys.exit(1)

# Variables globales

debug_enabled = False
pwd = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

json_alert = {}
now = time.strftime("%a %b %d %H:%M:%S %Z %Y")
# Rutas
log_file = '{0}/logs/integrations.log'.format(pwd)
socket_addr = '{0}/queue/sockets/queue'.format(pwd)

def main(args):
    debug("# Starting")
    # Leer argumentos de entrada del archivo ossec.conf
    alert_file_location = args[1]
    apikey = args[2]
    debug("# API Key")
    debug(apikey)
    debug("# File location")
    debug(alert_file_location)

    # Cargar alerta. Parsear objeto JSON
    with open(alert_file_location) as alert_file:
        json_alert = json.load(alert_file)
    debug("# Processing alert")
    debug(json_alert)

    # Pedir información de ChatGPT
    msg = request_chatgpt_info(json_alert,apikey)
    # Si hay una coincidencia, se envía al Servidor de Wazuh 
    if msg:
        send_event(msg, json_alert["agent"])
      
# Función para imprimir mensajes de depuración y registrarlos en un archivo de registro.
def debug(msg):
    if debug_enabled:
        msg = "{0}: {1}\n".format(now, msg)
        print(msg)
        f = open(log_file,"a")
        f.write(str(msg))
        f.close()

# Recopila información relevante de los datos obtenidos de ChatGPT.
def collect(data):
    full_log = data['full_log']
    content = data['content']
    return full_log, content

# Verifica si la información de la alerta está en la base de datos de ChatGPT.
def in_database(data, full_log):
    result = data['full_log']
    if result == 0:
        return False
    return True

# Realiza una consulta a la API de ChatGPT para obtener información relacionada con el registro completo proporcionado.
def query_api(full_log, apikey):
    headers = {
        'Authorization': 'Bearer ' + apikey,
        'Content-Type': 'application/json',
        'OpenAI-Beta': 'assistants=v2',
    }

    json_data = {
        "assistant_id": "XXXXXXX", # Poner el id del Asistente creado en la web de OpenAI API
        "thread": {
            "messages": [
                {"role": "user", "content": 'Regarding this log message, give me the IOCs of the event and more extra information' + full_log}
            ]
        }
    }
# 1º Se carga el mensaje en el asistente y se lanza. 
    response1 = requests.post('https://api.openai.com/v1/threads/runs', headers=headers, json=json_data)
# 2º Se obtiene el id del hilo generado por el asistente.  
    thread_id = response1.json()["thread_id"]
    time.sleep(10)
# 3º Se obtienen los mensajes del hilo generado.
    response2 = requests.get(f'https://api.openai.com/v1/threads/{thread_id}/messages', headers=headers)
# 4º Se obtiene el id del mensaje generado por el asistente que corresponde a first_id
    first_id = response2.json()["first_id"]
# 5º Se obtiene el contenido de la respuesta generada por el asistente.
    response = requests.get(f'https://api.openai.com/v1/threads/{thread_id}/messages/{first_id}', headers=headers)

    if response.status_code == 200:
        full_log = {"full_log": full_log}
        new_json = {}
        new_json = response.json()
        new_json.update(full_log)
        json_response = new_json

        data = json_response
        return data
    else:
        alert_output = {}
        alert_output["chatgpt"] = {}
        alert_output["integration"] = "custom-chatgpt"
        json_response = response.json()
        debug("# Error: The chatgpt encountered an error")
        alert_output["chatgpt"]["error"] = response.status_code
        alert_output["chatgpt"]["description"] = json_response["errors"][0]["detail"]
        send_event(alert_output)
        exit(0)

# Solicita información a ChatGPT utilizando la API y estructura los resultados en un formato de alerta.
def request_chatgpt_info(alert, apikey):
    alert_output = {}

    # Request info using chatgpt API
    data = query_api(alert["full_log"], apikey)

    # Create alert
    alert_output["chatgpt"] = {}
    alert_output["integration"] = "custom-chatgpt"
    alert_output["chatgpt"]["found"] = 0
    alert_output["chatgpt"]["source"] = {}
    alert_output["chatgpt"]["source"]["alert_id"] = alert["id"]
    alert_output["chatgpt"]["source"]["rule"] = alert["rule"]["id"]
    alert_output["chatgpt"]["source"]["description"] = alert["rule"]["description"]
    alert_output["chatgpt"]["source"]["full_log"] = alert["full_log"]

    full_log = alert["full_log"]

    # Check if chatgpt has any info about the full_log
    if in_database(data, full_log):
        alert_output["chatgpt"]["found"] = 1
    # Info about the IP found in chatgpt
    if alert_output["chatgpt"]["found"] == 1:
        full_log, content = collect(data)

        # Populate JSON Output object with chatgpt request
        alert_output["chatgpt"]["full_log"] = full_log
        alert_output["chatgpt"]["content"] = content

        debug(alert_output)

    return(alert_output)

# Envía un evento al Manager de Wazuh, incluyendo información sobre la alerta y los resultados obtenidos de ChatGPT.
def send_event(msg, agent = None):
    if not agent or agent["id"] == "000":
        string = '1:chatgpt:{0}'.format(json.dumps(msg))
    else:
        string = '1:[{0}] ({1}) {2}->chatgpt:{3}'.format(agent["id"], agent["name"], agent["ip"] if "ip" in agent else "any", json.dumps(msg))

    debug(string)
    sock = socket(AF_UNIX, SOCK_DGRAM)
    sock.connect(socket_addr)
    sock.send(string.encode())
    sock.close()

# Punto de entrada del script. Lee los argumentos de la línea de comandos, registra los errores y llama a la función principal.
if __name__ == "__main__":
    try:
        # Read arguments
        bad_arguments = False
        if len(sys.argv) >= 4:
            msg = '{0} {1} {2} {3} {4}'.format(now, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else '')
            debug_enabled = (len(sys.argv) > 4 and sys.argv[4] == 'debug')
        else:
            msg = '{0} Wrong arguments'.format(now)
            bad_arguments = True

        # Logging the call
        f = open(log_file, 'a')
        f.write(str(msg) + '\n')
        f.close()

        if bad_arguments:
            debug("# Exiting: Bad arguments.")
            sys.exit(1)

        # Main function
        main(sys.argv)

    except Exception as e:
        debug(str(e))
        raise
