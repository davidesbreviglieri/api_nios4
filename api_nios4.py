#==========================================================
#classe di gestione api nios4
#https://web.nios4.com/ws/doc/
#==========================================================
import requests
from typing import Optional, Dict, Any, List, Union
from datetime import datetime,timezone,date
from decimal import Decimal
from pathlib import Path
import uuid
import json
import os

class api_nios4:
    #--------------------------------------------------------
    def tid(self):
        #create tid (time id) using timezone 0
        val = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        #controllo che non mi finisca con un 60
        sval = str(int(val))
        if sval[-2:] == "60":
            val = val-1
        return int(val)
    #--------------------------------------------------------
    def reset_error(self):
        self.error_code = ""
        self.error_message = ""    
    #--------------------------------------------------------
    def check_value(self,value :Any,format : str):
        if format == "text":
            value = str(value) if value is not None else ""
        if format == "decimalnumber":
            if value == "":
                value = None
            value = float(Decimal(value)) if value is not None else 0
        if format == "integernumber":
            if value == "":
                value = None
            value = int(float(value)) if value is not None else 0
        if format == "date":
            if value is None or value == "":
                value = 0
            else:
                #converto la data
                value = self.normalize_date(value)
                #dt = datetime.strptime(value, "%Y-%m-%d")
                #formatvalue = dt.strftime("%Y%m%d%H%M%S")
                #value = int(formatvalue)            
        return value
    #--------------------------------------------------------        
    def normalize_tid(self,value):
        #converto un tid in una data effettiva
        dt = datetime.strptime(str(value), "%Y%m%d%H%M%S")
        return dt.isoformat()
    #--------------------------------------------------------        
    def normalize_date(self,value):
        """
        Rende `value` sempre un intero con formato YYYYMMDDHHMMSS.
        
        Se `value` è già un oggetto datetime/date o un intero,
        la funzione lo restituisce “come è”.
        Altrimenti assume che sia una stringa nel formato "%Y-%m-%d".
        """
        
        # 1. Se è già un datetime / date -> trasformalo in int
        if isinstance(value, (datetime, date)):
            dt = value   # già datetime o date
        elif isinstance(value, int):
            # si assume che l’intero sia già nel formato desiderato
            return value
        
        else:
            # 2. Altrimenti lo consideriamo una stringa di data
            try:
                dt = datetime.strptime(value, "%Y-%m-%d")
            except (ValueError, TypeError):
                raise ValueError(f"Non è possibile interpretare {value!r} come data")

        # 3. Ora convertiamo in formato intero YYYYMMDDHHMMSS
        return int(dt.strftime("%Y%m%d%H%M%S"))    
    #--------------------------------------------------------        
    def __init__(self,token:str = "",username:str = "",password:str=""):
        print("Inizializzo classe api nios4")
        
        self.base_url = 'https://web.nios4.com/ws/'
        self.reset_error()
        self.token = token
        self.id_user = ""  
        self.email_user = ""
        self.username = username
        self.password = password
        self.dbname = ""  
    #------------------------------------------------------------
    def login(self,token:str= ""):
        #eseguo il login
        self.reset_error()

        if token != "":
            self.token = token

        url = self.base_url + f'?action=user_login&email={self.username}&password={self.password}'
        if self.token != "":
            url = self.base_url + f'?action=user_login&token={self.token}'
                
        response= requests.get(url)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                return False
            else:
                #estrapolo i dati dell'utente
                utente = valori['user']
                self.id_user = utente['id']
                self.email_user = utente['email']
                if self.token == "":
                    self.token = utente['token']
                return True
        else:
            self.error_code = "E1"
            self.error_message = response.text
            return False
    #------------------------------------------------------------
    def database_list(self,token:str=""):
        #elenco dei database
        self.reset_error()

        if token != "":
            self.token = token
 
        if self.token != "":
            url = self.base_url + f'?action=database_list&token={self.token}'
        else:
            self.error_code = "E2"
            self.errormessage = "Token missing"
            return None
        
        response= requests.get(url)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                return None
            else:
                #estrapolo i dati dell'utente
                return valori['db']
        else:
            self.error_code = "E2"
            self.error_message = response.text
            return None     
    #------------------------------------------------------------
    def users_list(self,dbname:str="",token:str=""):
        #elenco dei database
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token

        if self.token != "":
            url = self.base_url + f'?action=users&token={self.token}&db={self.dbname}'
        else:
            self.error_code = "E2"
            self.error_message = "Token missing"
            return None
        
        response= requests.get(url)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                return None
            else:
                #estrapolo i dati dell'utente
                return valori['users']
        else:
            self.error_code = "E2"
            self.error_message = response.text
            return None     
    #------------------------------------------------------------
    def table_list(self,dbname:str="",token:str=""):
        #elenco dei database
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token

        if self.token != "":
            url = self.base_url + f'?action=table_list&token={self.token}&db={self.dbname}'
        else:
            self.error_code = "E2"
            self.error_message = "Token missing"
            return None
        
        response= requests.get(url)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                return None
            else:
                #estrapolo i dati dell'utente
                return valori['tables']
        else:
            self.error_code = "E2"
            self.error_message = response.text
            return None     
    #------------------------------------------------------------
    def table_info(self,tablename:str,dbname:str="",token:str=""):
        #dati tabella
        self.reset_error()

        if dbname != "":
            self.dbname = dbname        
        if token != "":
            self.token = token

        if self.token != "":
            url = self.base_url + f'?action=table_info&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.errorcode = "E2"
            self.errormessage = "Token missing"
            return None
        
        response= requests.get(url)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                return None
            else:
                #estrapolo i dati dell'utente
                return valori['table']
        else:
            self.error_code = "E2"
            self.error_message = response.text
            return None     
    #------------------------------------------------------------
    def fields_info(self,tablename:str,dbname:str="",token:str=""):
        #dati tabella
        self.reset_error()

        if dbname != "":
            self.dbname = dbname        
        if token != "":
            self.token = token

        if self.token != "":
            url = self.base_url + f'?action=table_info&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.errorcode = "E2"
            self.errormessage = "Token missing"
            return None
        
        response= requests.get(url)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                return None
            else:
                #estrapolo i dati dell'utente
                return valori['fields']
        else:
            self.error_code = "E2"
            self.error_message = response.text
            return None     
    #------------------------------------------------------------
    def get_record(self,tablename:str,gguid:str,dbname:str="",token:str=""):
        #recupero un record specifico
        self.reset_error()
        if dbname != "":
            self.dbname = dbname        
        if token != "":
            self.token = token
        #creo il payload
        if self.token != "":
            url = self.base_url + f'?action=model&token={self.token}&db={self.dbname}&tablename={tablename}&gguid={gguid}'
        else:
            self.error_code = "E2"
            self.error_message = "Token missing"
            return None
        response= requests.get(url)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                return None
            else:
                #estrapolo i dati dell'utente
                return valori['records']
        else:
            self.error_code = "E2"
            self.error_message = response.text
            return None
    #------------------------------------------------------------
    def detail_delete(self,tablename:str,gguid:str,dbname:str ="",token:str=""):
        #eseguo l'eliminazione profonda del rapportino
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token

        if gguid == "":
            return None

        payload = {}
        payload['tablename'] = tablename
        payload['gguid'] = gguid

        url = ""
        if self.token != "":
            url = self.base_url + f'?action=detail_delete&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.error_code = "E2"
            self.error_message = "Token missing"
            return None
        response= requests.post(url, json=payload)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                #print(self.errormessage)
                return None
            else:
                #estrapolo i dati dell'utente
                return valori
        else:
            self.error_code = "E2"
            self.error_message = response.text
            #print(self.errormessage)
            return None   
    #------------------------------------------------------------
    def detail_resolve(self,tablename:str,gguid:str,dbname:str ="",token:str=""):
        #eseguo una forzatura di ricalcolo complata su un dettaglio
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token

        payload = {}
        payload['tablename'] = tablename
        payload['gguid'] = gguid

        url = ""
        if self.token != "":
            url = self.base_url + f'?action=detail_resolve&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.error_code = "E2"
            self.error_message = "Token missing"
            return None
        response= requests.post(url, json=payload)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                #print(self.errormessage)
                return None
            else:
                #estrapolo i dati dell'utente
                return valori
        else:
            self.error_code = "E2"
            self.error_message = response.text
            #print(self.errormessage)
            return None   

    #------------------------------------------------------------
    def fuzzy_records(self,tablename:str,fields_search: List[str],fields_return: List[str],query:str,dbname:str ="",token:str="",threshold:Decimal=0.5):
        #eseguo una ricerca semantica su un valore
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token

        payload = {}
        payload['fields'] = fields_return
        fuzzy = {}
        fuzzy['fields'] = fields_search
        fuzzy['query'] = query
        fuzzy['threshold'] = threshold
        payload['fuzzy'] = fuzzy

        url = ""
        if self.token != "":
            url = self.base_url + f'?action=model_fuzzy&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.error_code = "E2"
            self.error_message = "Token missing"
            return None

        response= requests.post(url, json=payload)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                #print(self.errormessage)
                return None
            else:
                #estrapolo i dati dell'utente
                return valori['results']
        else:
            self.error_code = "E2"
            self.error_message = response.text
            #print(self.errormessage)
            return None   
    #------------------------------------------------------------
    def find_records(self,tablename:str,dbname:str="",token:str="",fields_search: List[str] = None,value_search: str = ""): 
        #procedo a cercare uno specifico record
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token
        '''
        payload = {
            "search": {
                "fields": ["state_document"],
                "query": "Open"
            }
        }
        '''
        payload = {}
        if fields_search != None and value_search != "":
            payload["search"] = {
                "fields": fields_search,
                "query": value_search
            }
        #print(payload)
        url = ""
        if self.token != "":
            url = self.base_url + f'?action=model&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.error_code = "E2"
            self.error_message = "Token missing"
            return None
        #print(url)
        response= requests.post(url, json=payload)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                #print(self.errormessage)
                return None
            else:
                #estrapolo i dati dell'utente
                return valori['records']
        else:
            self.error_code = "E2"
            self.error_message = response.text
            #print(self.errormessage)
            return None        
    #------------------------------------------------------------
    def save_record(self,tablename: str,values: Dict[str, Any],dbname: str ="",token:str="",is_new:bool=True,delete:bool=False):
        #procedo a salvare un record
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token
        #se i valori["gguid"] è vuoto non salvo il record
        if values["gguid"] == "" or values["gguid"] == None:
            self.error_code = "E1" 
            self.error_message = "Non è definito il gguid del record"
            return None
        #creo il payload
        payload = {
            "is_new": is_new,
            "values": values,
            "delete": delete,
        }
        #procedo a inviare il record
        url = ""
        if self.token != "":
            url = self.base_url + f'?action=detail_save&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.error_code = "E2"
            self.error_message = "Token missing"
            return None
        response= requests.post(url, json=payload)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                return None
            else:
                #estrapolo i dati dell'utente
                return valori
    #------------------------------------------------------------
    def save_records(self,tablename: str,values: List[Dict[str, Any]],dbname: str ="",token:str=""):
        #procedo a salvare un record
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token
        #se i valori["gguid"] è vuoto non salvo il record
        if values["gguid"] == "" or values["gguid"] == None:
            self.error_code = "E1" 
            self.error_message = "Non è definito il gguid del record"
            return None
        #creo il payload
        payload = {
            "rows": values
        }
        #procedo a inviare il record
        url = ""
        if self.token != "":
            url = self.base_url + f'?action=table_save&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.error_code = "E2"
            self.error_message = "Token missing"
            return None
        response= requests.post(url, json=payload)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                return None
            else:
                #estrapolo i dati dell'utente
                return valori
    #------------------------------------------------------------
    def create_data_file(self,filename:str,gguidrif:str="") -> tuple[str, str]:
        #creo la stringa per salvare correttamente i dati di un file
        #normalizzo il nome del file se per caso contiene il percorso
        onlyfilename = os.path.basename(filename)
        if gguidrif == "":
            gguidrif = str(uuid.uuid4())
        d1 = {
            "gguidfile": gguidrif,
            "nomefile": onlyfilename
        }        
        body = json.dumps(d1)
        return gguidrif,body
    #------------------------------------------------------------
    def download_file(self,path:str,gguidrif:str,tablename:str, dbname: str ="",token:str="") -> bool:
        #recupero un file dal server
        self.reset_error()
        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token        

        url = ""
        if self.token != "":
            url = f'https://app.pocketsell.com/_sync/?action=file_download&token={self.token}&db={self.dbname}&tablename={tablename}&gguid={gguidrif}'
        else:
            self.error_code = "E2"
            self.error_message = "Token missing"
            return False
        print(url)
        try:
            response = requests.get(url, stream=True)
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # ignora keep-alive chunks
                        f.write(chunk)
        except requests.RequestException as e:
            self.error_code = "F1"
            self.error_message = str(e)
            print(f"HTTP error: {e}")
        except ValueError:
            # JSON non valido
            print(f"Response non-JSON: {response.text[:500]}")
        return True        

    #------------------------------------------------------------
    def upload_file(self,path:str,is_image:bool,gguidrif:str,tablename:str, dbname: str ="",token:str="") -> bool:
        #invio un file al server
        self.reset_error()
        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token        

        type = "image"
        if is_image == False:
            type = "file"

        data = Path(path).read_bytes()

        url = ""
        if self.token != "":
            url = f'https://app.pocketsell.com/_sync/?action=file_upload&token={self.token}&db={self.dbname}&tablename={tablename}&gguid={gguidrif}&type={type}'
        else:
            self.error_code = "E2"
            self.error_message = "Token missing"
            return False

        try:
            # In VB non veniva impostato il Content-Type; con raw byte va bene octet-stream
            resp = requests.post(url, data=data, headers={"Content-Type": "application/octet-stream"}, timeout=30)
            resp.raise_for_status()

            valori = resp.json()  # deve restituire un JSON con chiave "result"
            return valori.get("result") != "KO"
        except requests.RequestException as e:
            self.error_code = "F1"
            self.error_message = str(e)
            print(f"HTTP error: {e}")
        except ValueError:
            # JSON non valido
            print(f"Response non-JSON: {resp.text[:500]}")
        return True
        
    #------------------------------------------------------------
    def sync(self,dbname: str ="",token:str=""):
        #forzo la sincronizzazione
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token

        #procedo a inviare il record
        if self.token != "":
            url = self.base_url + f'?action=sync&token={self.token}&db={self.dbname}'
        else:
            self.error_code = "E2"
            self.error_message = "Token missing"
            return None
        response= requests.get(url)
        if response.status_code == 200:
            valori= response.json()
            if valori["error"] == True:
                self.error_code = valori["error_code"]
                self.error_message = valori["error_message"]
                return None
            else:
                #estrapolo i dati dell'utente
                #print(valori)
                return valori

