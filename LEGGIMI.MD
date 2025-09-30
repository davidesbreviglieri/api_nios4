# api_nios4 — Python wrapper per Nios4 Web API

Una piccola libreria Python (singolo file) per interagire con il backend **Nios4** tramite le *Web API* ufficiali. Fornisce funzioni di autenticazione, lettura/scrittura record, ricerche testuali e fuzzy, gestione file (upload/download) e sincronizzazione.

> **Documentazione ufficiale API Nios4**: https://en.nios4.dev/wep-api

---

## Indice
- [Premessa e contesto](#premessa-e-contesto)
- [Caratteristiche principali](#caratteristiche-principali)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
- [Primi passi (Quickstart)](#primi-passi-quickstart)
- [Concetti chiave](#concetti-chiave)
- [Esempi d'uso](#esempi-duso)
  - [Autenticazione e database](#autenticazione-e-database)
  - [Tabelle e campi](#tabelle-e-campi)
  - [Lettura record](#lettura-record)
  - [Ricerca testuale e fuzzy](#ricerca-testuale-e-fuzzy)
  - [Creazione/Aggiornamento/Eliminazione record](#creazioneaggiornamentoeliminazione-record)
  - [Gestione file (upload/download)](#gestione-file-uploaddownload)
  - [Sincronizzazione](#sincronizzazione)
- [Riferimento API (metodi)](#riferimento-api-metodi)
- [Error handling](#error-handling)
- [Best practice](#best-practice)
- [Limitazioni note](#limitazioni-note)
- [Sicurezza](#sicurezza)
- [Contribuire](#contribuire)
- [Licenza](#licenza)

---

## Premessa e contesto
Il sistema cloud di **Nios4** si basa su due tipologie di database:

1. **Database di sincronizzazione (D-One Syncone)**: i dati transitano via server di sincronizzazione D‑One e sono formattati come stringhe JSON per l’archiviazione e lo scambio tra dispositivi. Questo permette di avere tabelle identiche indipendentemente dai dati contenuti.
2. **Database cloud della versione web**: i dati sono salvati nei rispettivi campi e tabelle ed utilizzati direttamente dal front‑end web.

Le **Web API di Nios4** sono progettate per leggere e scrivere **direttamente** sul database della versione web.

Questa libreria incapsula le chiamate HTTP principali, offrendo helper per normalizzazione date/TID, ricerche, e operazioni CRUD.

---

## Caratteristiche principali
- **Login** via *token* o *username/password*.
- **Elenco database, utenti, tabelle** e **metadati tabella/campi**.
- **Lettura record** (singoli e liste con filtri/ordinamenti).
- **Ricerca fuzzy semantica** su più campi con soglia configurabile.
- **CRUD**: salvataggio di singolo record o batch, cancellazione dettagliata e *resolve* (ricalcolo espressioni).
- **Gestione file**: upload/download di FILE/IMAGE collegati ai record.
- **Sync**: innesco della sincronizzazione con supporto partial sync.
- Helper utility: `tid()`, `normalize_tid()`, `normalize_date()`, `check_value()` e creazione payload file.

---

## Requisiti
- Python 3.10+
- Dipendenze: `requests`

```bash
pip install requests
```

---

## Installazione
Copia il file `api_nios4.py` nel tuo progetto oppure installalo come modulo interno.

```bash
# esempio struttura
your-project/
  ├─ api_nios4.py
  └─ app.py
```

---

## Primi passi (Quickstart)
```python
from api_nios4 import api_nios4

# istanzia il client (puoi passare token oppure username/password)
client = api_nios4(username="user@example.com", password="secret")

# login: aggiorna token, id_user, email_user
if not client.login():
    raise RuntimeError(f"Login fallito: {client.error_code} - {client.error_message}")

# elenca i database disponibili
dbs = client.database_list()
print(dbs)

# seleziona un database e leggi le tabelle
client.dbname = dbs[0]["dbname"]
print(client.table_list())
```

---

## Concetti chiave
- **TID** (*Time Identifier*): intero `YYYYMMDDHHMMSS` in UTC. Utile per ordinamenti e filtri temporali.
  - `tid()` → genera TID corrente.
  - `normalize_tid(tid_int)` → ISO 8601 `YYYY-MM-DDTHH:MM:SS`.
  - `normalize_date(value)` → converte `datetime`, `date`, `int` o stringa `YYYY-MM-DD` in TID (`int`).
- **check_value(value, format)**: normalizza valori in base al tipo campo (`text`, `decimalnumber`, `integernumber`, `date`).

---

## Esempi d'uso

### Autenticazione e database
```python
client = api_nios4(username="user@example.com", password="secret")
assert client.login()

# oppure con token già noto
client = api_nios4(token="<TOKEN>")
assert client.login()

# database disponibili
dbs = client.database_list()
for db in dbs:
    print(db["dbname"], db.get("description"))

client.dbname = dbs[0]["dbname"]
```

### Tabelle e campi
```python
# elenco tabelle
tables = client.table_list()

# info tabella (parametri, expressions, styles)
info = client.table_info("customers")

# campi e metadati
fields = client.fields_info("customers")
```

### Lettura record
```python
# singolo record per gguid
row = client.get_record("customers", gguid="550e8400-e29b-41d4-a716-446655440000")

# lista record con ricerca semplice e filtri
rows = client.find_records(
    tablename="customers",
    fields_search=["name", "surname"],
    value_search="doe",
    search_by={"email": "@acme.com"},     # LIKE
    conditions={"status": ["active", "trial"]},  # = / IN
    order_info=[["created_at", True]]      # True = ASC, False = DESC
)
```

### Ricerca testuale e fuzzy
```python
# fuzzy su più campi con soglia
results = client.fuzzy_records(
    tablename="customers",
    fields_search=["name", "surname", "company"],
    fields_return=["gguid", "name", "surname", "email"],
    query="jon",               # es: match con "John", "Jonathon"...
    threshold=0.7,
    search_by={"email": "@acme.com"},
)
```

### Creazione/Aggiornamento/Eliminazione record
```python
from uuid import uuid4

# crea nuovo record
record = {
    "gguid": str(uuid4()),
    "name": "Alice",
    "surname": "Bianchi",
}
result = client.save_record("customers", record, is_new=True)

# aggiorna record esistente
record["name"] = "Alice Updated"
result = client.save_record("customers", record, is_new=False)

# elimina record e dettagli collegati
client.detail_delete("customers", gguid=record["gguid"])  # soft via endpoint dedicato

# forza ricalcolo espressioni/valori
client.detail_resolve("orders", gguid="...")
```

### Gestione file (upload/download)
```python
# prepara metadata file (gguidfile + nomefile)
gguidfile, body = client.create_data_file("/path/to/report.pdf")

# upload come file generico (non immagine)
success = client.upload_file(
    path="/path/to/report.pdf",
    is_image=False,
    gguidrif=gguidfile,
    tablename="documents"
)

# download
ok = client.download_file(
    path="./report.pdf",
    gguidrif=gguidfile,
    tablename="documents"
)
```

### Sincronizzazione
```python
sync_info = client.sync()
if sync_info and sync_info.get("sync", {}).get("partial"):
    print("Partial sync attiva. Continua da:", sync_info["sync"]["partial_from"])
```

---

## Riferimento API (metodi)
> **Nota**: quasi tutti i metodi accettano opzionalmente `dbname` e/o `token` per override runtime.

- **`login(token: str="") -> bool`**
  Autentica l’utente via token o username/password. Aggiorna `token`, `id_user`, `email_user`.

- **`database_list(token: str="") -> Optional[list]`**
  Elenco database disponibili per l’utente autenticato.

- **`users_list(dbname: str="", token: str="") -> Optional[list]`**
  Utenti associati al database (`UTA`).

- **`table_list(dbname: str="", token: str="") -> Optional[list]`**
  Elenco tabelle nel database.

- **`table_info(tablename: str, dbname: str="", token: str="") -> Optional[dict]`**
  Metadati tabella: parametri, expressions, styles.

- **`fields_info(tablename: str, dbname: str="", token: str="") -> Optional[list]`**
  Metadati dei campi della tabella.

- **`get_record(tablename: str, gguid: str, ...) -> Optional[list]`**
  Ritorna il record (lista contenente un dict) per `gguid`.

- **`find_records(tablename: str, ..., fields_search: List[str]|None, value_search: str="", search_by: dict|None, conditions: dict|None, order_info: list|None, iduser: str="") -> Optional[list]`**
  Query record con ricerca testuale, filtri LIKE/IN e ordinamenti.

- **`fuzzy_records(tablename: str, fields_search: List[str], fields_return: List[str], query: str, ..., threshold: Decimal=0.5, search_by: dict|None, conditions: dict|None, iduser: str="") -> Optional[list]`**
  Ricerca fuzzy/semantica su più campi con soglia [0.0–1.0].

- **`save_record(tablename: str, values: Dict[str, Any], ..., is_new: bool=True, delete: bool=False) -> Optional[dict]`**
  Salva (insert/update) o elimina (`delete=True`) un singolo record. `values` **deve** contenere `gguid`.

- **`save_records(tablename: str, values: List[Dict[str, Any]], ...) -> Optional[dict]`**
  Salva in batch più record. Ogni record **deve** contenere `gguid`.

- **`detail_delete(tablename: str, gguid: str, ...) -> Optional[dict]`**
  Elimina il record e i dettagli collegati (link tables).

- **`detail_resolve(tablename: str, gguid: str, ...) -> Optional[dict]`**
  Forza il ricalcolo di espressioni e distributori di valori.

- **`create_data_file(filename: str, gguidrif: str="") -> Tuple[str, str]`**
  Genera `gguidfile` e JSON metadata (`nomefile`) per registrare un file.

- **`upload_file(path: str, is_image: bool, gguidrif: str, tablename: str, ...) -> bool`**
  Carica file/immagine al sincronizzatore (sovrascrive se `gguid` esiste).

- **`download_file(path: str, gguidrif: str, tablename: str, ...) -> bool`**
  Scarica file grezzo e lo salva su disco.

- **`sync(dbname: str="", token: str="") -> Optional[dict]`**
  Forza la sincronizzazione con supporto *partial sync*.

- **Utility**
  - `tid() -> int`: genera TID UTC `YYYYMMDDHHMMSS` (con fix su secondi `60`).
  - `normalize_tid(value: int) -> str`: TID → ISO 8601.
  - `normalize_date(value: Any) -> int`: normalizza date verso TID.
  - `check_value(value: Any, format: str) -> Any`: normalizza valori per tipo campo.

---

## Error handling
Ogni metodo resetta lo stato d’errore con `reset_error()` e, in caso di failure, valorizza:

- `self.error_code`: codice interno o passato dal server (es. `TK1` per token mancante).
- `self.error_message`: messaggio descrittivo o payload HTTP.

Pattern consigliato:
```python
res = client.table_list()
if res is None:
    print("Errore:", client.error_code, client.error_message)
```

Codici interni tipici (non esaustivo):
- `TK1`: token mancante.
- `E1`–`E11`: errori generici per endpoint specifici.
- `F1`: errori file/I/O o HTTP durante upload/download.

Il server può restituire `error: True` con `error_code`/`error_message` propri.

---

## Best practice
- **Gestisci il token**: dopo `login()` conserva `client.token` per sessioni successive.
- **Imposta `dbname`** prima delle chiamate legate ai dati (`client.dbname = "..."`).
- **Controlla sempre gli errori**: verifica `None`/`False` e leggi `error_code`/`error_message`.
- **Normalizza i valori**: usa `check_value()` per rispettare i tipi dei campi.
- **Genera `gguid` client-side** per nuovi record (`uuid4()`).
- **Batch writing**: preferisci `save_records()` quando inserisci molti record.
- **File grandi**: gestisci con cautela timeout e spazio disco; per immagini imposta `is_image=True`.
- **Rate/Retry**: in caso di `partial sync`, implementa retry/backoff lato client.

---

## Limitazioni note
- **`save_records`**: l’implementazione corrente effettua un controllo `values["gguid"]` che presuppone `values` sia un `dict`. Dato che la firma prevede una *lista di dict*, si consiglia di:
  - correggere il controllo iterando sulla lista, **oppure**
  - rimuovere il controllo e delegarlo al server.

- **`tid()`**: il fix sui secondi `"60"` sottrae `1` ad una stringa castata a `int`; in casi limite potrebbe essere più robusto convertire prima a `datetime` e gestire rollover.

- **`download_file`/`upload_file`**: usano endpoint su `app.pocketsell.com/_sync`; verificare coerenza con ambienti/istanze on‑prem o custom.

Contribuzioni per migliorare questi punti sono benvenute (vedi sotto).

---

## Sicurezza
- Non committare credenziali: usa variabili d’ambiente o secret manager.
- Usa **HTTPS** (già previsto dagli endpoint) e gestisci eccezioni `requests`.
- Per dati personali, valuta politiche di minimizzazione e audit dei log.

---

## Contribuire
1. Forka il repository.
2. Crea un branch: `git checkout -b feature/nome-funzione`.
3. Aggiungi test e docstring dove possibile.
4. Apri una Pull Request descrivendo chiaramente le modifiche.

Per bug report, usa le *Issues* includendo:
- versione Python,
- traceback completo,
- snippet riproducibile,
- eventuale risposta dell’API (omettendo dati sensibili).

---

## Licenza
Il file include un *BSD‑like disclaimer*. Salvo indicazioni diverse nel repository, considera la licenza **BSD‑2-Clause**. Vedi l’intestazione del sorgente per i termini esatti.

