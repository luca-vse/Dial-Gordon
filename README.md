
# Dial Gordon
Gordon is a bot created to control voicemail. Gordon helps with reading and answering voicemail messages. Bot uses Rasa Open Source Framework, FastAPI, Google Chrome extensition for TTS and STT and a database in XAMPP that simulates voicemail. Bot understands English.

Gordon je bot vytvořen pro ovládání hlasové schránky. Gordon pomáhá s čtením a odpovídáním na zprávy z hlasové schránky. Je sestaven za pomoci Rasa Open Source Framework, FastAPI, rozšíření pro Google Chrome pro TTS a STT a databáze v XAMPP, která simuluje hlasovou schránku. Bot umí anglicky.


## Náhled aplikace
![botGordonGit](https://github.com/luca-vse/Dial-Gordon/assets/147036440/722ad174-daa6-4948-a4e8-9e19d5b01df2)

## Funkce

- Hlasové a textové ovládání
- Čtení nových zpráv (po pořadě, dle jména, dle priority)
- Odpovídání na zprávy (zavoláním zpět, přidáním události do kalendáře, zablokování volajícího, smazání zpráv)
- Nastavení uvítací zprávy
- Změna a reset pinu
- Zopakování zprávy od bota
- Pozdravení, poděkování, rozloučení
- Zobrazení nápovědy


## Instalace
Prerekvizity: Nainstalován Python 3.8.10, pip3, Rasa 3.6.2, modul XAMPP s databází uvedenou ve složce Db_data. 
Projekt je spouštěn z VS Code na Windows 10 Pro. Aplikaci lze spustit lokálně nebo vytvořit kontejner v dockeru.

    
## Spuštění lokálně

Naklonovat projekt

```bash
  git clone https://github.com/luca-vse/Dial-Gordon.git
```

Přepnout z aktuálního adresáře do adresáře Dial-Gordon
```bash
  cd Dial-Gordon
```

Pro instalaci balíčků závislostí spustit následující příkazy
```bash
  pip install rasa-sdk
  pip install mysql-connector-python
  pip install bcrypt
  pip install google-auth google-auth-oathlib google-auth-httplib2
  pip install google-api-python-client
  pip install pydantic fastapi requests uvicorn
  pip install python-dateutil
```

Přidat do souboru hosts nacházejícího se C:\Windows\System32\drivers\etc\hosts
```bash
127.0.0.1 rasa_actions
127.0.0.1 rasa_api
```

Pro spuštění aplikace zadat příkazy
```bash
  rasa train
  rasa run actions
  rasa run --verbose --enable-api
  uvicorn app.app:app --reload --port 8000
```
V prohlížeči Google Chrome pro zobrazení aplikace zadat localhost:8000

## Vytvoření kontejneru v Dockeru
Potřeba mít nainstalovaný docker

```bash
  docker compose up --build
```


