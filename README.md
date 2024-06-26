# Implantación y diseño de un sistema de detección de insiders mediante Wazuh

Este repositorio contiene los scripts y configuraciones utilizados en el desarrollo del Trabajo de Fin de Grado (TFG) centrado en el diseño y desarrollo de un sistema para detectar "insiders" (usuarios internos malintencionados) mediante la recopilación y análisis de registros del sistema y la caracterización de amenazas.

## Descripción

1) Implementación y Configuración de Wazuh: Concentración en la implementación y configuración de la herramienta Wazuh, un sistema de detección de amenazas y seguridad basada en código abierto.
2) Desarrollo de Reglas y Patrones: Formulación de reglas y patrones específicos para identificar comportamientos anómalos o acciones sospechosas realizadas por usuarios internos.
3) Integración de Inteligencia Artificial: Investigación y desarrollo de una solución que habilite la aplicación de inteligencia artificial en la identificación y caracterización de amenazas, tales como los Indicadores de Compromiso (IoC).

## Empezando 🚀

Estas instrucciones te guiarán para obtener una copia de este proyecto en funcionamiento en tu máquina local para propósitos de desarrollo y pruebas.

### Software utilizado 📋

Lista de software y herramientas utilizados, incluyendo versiones:

1. Sistemas Operativos:
   - Microsoft Windows: Windows 11 PRO v10.0.22631 tanto en equipo de trabajo como en la máquina virtual
   - GNU/Linux: Ubuntu 22.04.3 LTS
3. Virtualización/Contenedores:
   - VirtualBox


## Instalación 🔧

#### Wazuh Indexer

```bash
curl -sO https://packages.wazuh.com/4.7/wazuh-install.sh
curl -sO https://packages.wazuh.com/4.7/config.yml

```
Se debe editar el `config.yml` con el nombre de los nodos y su dirección IP.
<p align="center"><img src="indexer-config.yml.png"/></p> 

Después se ejecuta el asistente de instalación de Wazuh con la opción `--generate-config-files` para  generar la clave del clúster, los certificados y las contraseñas de Wazuh necesarios para la instalación
```bash
bash wazuh-install.sh --generate-config-files
```
Se copia el archivo llamado `wazuh-install-files.tar` en todos los servidores de la implementación distribuida, incluidos el server, el indexer y el dashboard.
Ahora para cada nodo indexador: descargamos el instalador de wazuh
```bash
curl -sO https://packages.wazuh.com/4.7/wazuh-install.sh
```
Se ejecuta el instalador de Wazuh con el nombre del nodo indexer y se inicia el cluster
```bash
bash wazuh-install.sh --wazuh-indexer <WAZUH_INDEXER_NAME>
bash wazuh-install.sh --start-cluster
```
Ahora se debe obtener la contraseña de administrador para comprobar su correcto funcionamiento:
```bash
tar -axf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt -O | grep -P "\'admin\'" -A 1
```
Obtenida la contraseña se ejecuta lo siguiente de forma separada cambiando los valores que corresponden:
```bash
curl -k -u admin:<ADMIN_PASSWORD> https://<WAZUH_INDEXER_IP>:9200
curl -k -u admin:<ADMIN_PASSWORD> https://<WAZUH_INDEXER_IP>:9200/_cat/nodes?v
```
#### Wazuh Server

Se descarga el instalador de Wazuh en el servidor
```bash
curl -sO https://packages.wazuh.com/4.7/wazuh-install.sh
```
Y ahora se ejecuta el instalador de Wazuh con el nombre del nodo servidor , si se requieren más servidores se ejecuta el mismo comando
```bash
bash wazuh-install.sh --wazuh-server <WAZUH_SERVER_NAME>
```

#### Wazuh Dashboard

Se descarga el instalador de Wazuh en el dashboard
```bash
curl -sO https://packages.wazuh.com/4.7/wazuh-install.sh
```
Y ahora ejecutamos el instalador de Wazuh con el nombre del nodo dashboard que se especificó en el fichero `config.yml'
```bash
bash wazuh-install.sh --wazuh-dashboard <WAZUH_DASHBOARD_NAME> 
```
Después se deben obtener las contraseñas para acceder al dashboard.
```bash
tar -O -xvf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt 
```

#### Wazuh Agent
Para instalar un agente en cualquier sistema, se requiere tener la dirección IP donde se ejecutará el agente y conocer el sistema operativo correspondiente. Una vez que se disponen de estos parámetros, desde el panel de control de Wazuh se proporciona un comando que debe ejecutarse en el agente para iniciarlo.

## Aspectos a tener en cuenta ⚙️
Para iniciar y arrancar las máquinas se debe hacer en el siguiente orden:
1º Server
2ª Indexer
3º Dashboard

Para consultar el estado de los distintos componentes se deben ejecutar los siguientes comandos en su correspondiente máquina virtual.
```bash
systemctl status wazuh-manager #Consultar el estado del Server
systemctl status wazuh-indexer #Consultar el estado del Indexer
systemctl status wazuh-dashboard #Consultar el estado del Dashboard
```
Para cualquier cambio que se haga en local.rules, ossec.conf, integrations y demás archivos que impliquen un cambio de funcionamiento deberán aplicarse mediante el siguiente comando.
```bash
systemctl restart wazuh-manager 
```

## Construido Con 🛠️

Los scripts han sido realizados en Python
- [Python](https://www.learnpython.org/es/) - El lenguaje utilizado

## Roadmap

La tendencia para la mejora de este proyecto radica en el entrenamiento del asistente de OpenAI, a mayor entrenamiento, documentos e intrucciones añadidas mejro será Wazuh.

## Autores ✒️

- **Mario Muñoz** - [Mario M](https://github.com/mariocebre7)


