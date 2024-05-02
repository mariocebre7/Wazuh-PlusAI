#### Aspectos importantes
Se deben dar permisos de ejecución a todas las integraciones que vayan a ser utilizadas, por ejemplo:
```bash
chmod 750 /var/ossec/integrations/custom-telegram*
chown root:ossec /var/ossec/integrations/custom-telegram*
```
Y hay que especificar en la configuración de Wazuh que se cuenta con una integración. En el archivo `/var/ossec/etc/ossec.conf` hay que añadir lo siguiente:
```xml
<integration>
        <name>custom-telegram</name>
        <level>3</level>
        <hook_url>https://api.telegram.org/bot*API KEY*/sendMessage</hook_url>
        <alert_format>json</alert_format>
</integration>
```
