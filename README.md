
# Dial Gordon
Gordon is a bot build using Rasa Open Source Framework and FastAPI. Gordon is useful for reading and answering voicemail messages. Bot helps with reading and responding to messages from voicemail. Protype but is capable and knows english.

Gordon je bot vytvořen pro ovládání hlasové schránky. Je sestaven za pomoci Rasa Open Source Framework, FastAPI, rozšíření pro Google Chrome pro TTS a STT a databáze v XAMPP, která simuluje hlasovou schránku. Bot umí anglicky.


## Screenshots

![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)


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
Prerekvizity: Nainstalován Python 3.8.10, pip3, Rasa 3.6.2, modul XAMPP s databází uvedenou ve složce XXX. 
Projekt je spouštěn z VS Code na Windows 10 Pro. Aplikaci lze spustit lokálně nebo vytvořit kontejner v dockeru.

    
## Spuštění lokálně

Naklonování projektu

```bash
  git clone https://github.com/luca-vse/Dial-Gordon.git
```

Nainstalování závislostí

```bash
  pip install rasa-sdk
  pip install mysql-connector-python
  pip install bcrypt
  pip install google-auth google-auth-oathlib google-auth-httplib2
  pip install google-api-python-client
  pip install pydantic fastapi requests uvicorn
  pip install python-dateutil
```

Pro spuštění aplikace. V Chromu zadat localhost:8000

```bash
  rasa train
  rasa run actions
  rasa run --verbose --enable-api
  uvicorn app.app:app --reload --port 8000
```


## Vytvoření kontejneru v Dockeru
Potřeba mít nainstalovaný docker.

```bash
  docker compose up --build
```


