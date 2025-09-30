#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#================================================================================
#Copyright of Davide Sbreviglieri 2024
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
#================================================================================
#API NIOS4
#================================================================================
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
    def tid(self) -> int:
        """
        Generate a unique time-based identifier (TID) in UTC timezone.

        The identifier is created from the current UTC time in the format
        ``YYYYMMDDHHMMSS``. If the generated value ends with "60" (an invalid
        second value), it is adjusted by subtracting 1.

        Returns
        -------
        int
            The generated time identifier as an integer.

        Examples
        --------
        >>> obj.tid()
        20250930143215
        """
        val = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        #I check that the value does not end with 60
        sval = str(int(val))
        if sval[-2:] == "60":
            val = val-1
        return int(val)
    #--------------------------------------------------------
    def reset_error(self):
        """
        Reset error message
        """
        self.error_code = ""
        self.error_message = ""    
    #--------------------------------------------------------
    def check_value(self,value :Any,format : str) -> Any:
        """
        Validate and normalize a value according to the specified format.

        Depending on the given format, the function converts the input value
        into a standardized type:
        
        - ``text``: Converts the value to a string (empty string if None).
        - ``decimalnumber``: Converts to a float using Decimal, or 0 if None/empty.
        - ``integernumber``: Converts to an integer, or 0 if None/empty.
        - ``date``: Converts to a normalized date using ``self.normalize_date``,
        or 0 if None/empty.

        Parameters
        ----------
        value : Any
            The input value to validate and normalize.
        format : str
            The expected format of the value. Supported options are:
            ``"text"``, ``"decimalnumber"``, ``"integernumber"``, ``"date"``.

        Returns
        -------
        Any
            The normalized value, with its type depending on the specified format.

        Examples
        --------
        >>> obj.check_value("123.45", "decimalnumber")
        123.45

        >>> obj.check_value("", "integernumber")
        0

        >>> obj.check_value(None, "text")
        ''

        >>> obj.check_value("2025-09-30", "date")
        20250930
        """        
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
                value = self.normalize_date(value)
        return value
    #--------------------------------------------------------        
    def normalize_tid(self, value: int) -> str:
        """
        Convert a numeric time identifier (TID) into an ISO 8601 datetime string.

        The input value is expected to be in the format ``YYYYMMDDHHMMSS`` and will
        be parsed into a Python ``datetime`` object, which is then converted into
        ISO 8601 string representation.

        Parameters
        ----------
        value : int
            The time identifier in the format ``YYYYMMDDHHMMSS``.

        Returns
        -------
        str
            The corresponding datetime in ISO 8601 format.

        Examples
        --------
        >>> obj.normalize_tid(20250930143215)
        '2025-09-30T14:32:15'
        """        
        dt = datetime.strptime(str(value), "%Y%m%d%H%M%S")
        return dt.isoformat()
    #--------------------------------------------------------        
    def normalize_date(self, value: Any) -> int:
        """
        Normalize a date or datetime into a numeric time identifier (TID).

        The function accepts different types of inputs and converts them
        into an integer timestamp in the format ``YYYYMMDDHHMMSS``:

        - ``datetime`` or ``date`` objects: converted directly.
        - ``int`` values: returned as-is (assumed already normalized).
        - ``str`` values: parsed as ``YYYY-MM-DD``.
        
        If the input string cannot be parsed as a date, a ``ValueError`` is raised.

        Parameters
        ----------
        value : Any
            The input value to normalize. Supported types are ``datetime``,
            ``date``, ``int``, or ``str`` in the format ``YYYY-MM-DD``.

        Returns
        -------
        int
            The normalized date as an integer in the format ``YYYYMMDDHHMMSS``.

        Raises
        ------
        ValueError
            If the string input cannot be parsed as a valid date.

        Examples
        --------
        >>> obj.normalize_date(datetime(2025, 9, 30, 14, 32, 15))
        20250930143215

        >>> obj.normalize_date(date(2025, 9, 30))
        20250930000000

        >>> obj.normalize_date(20250930143215)
        20250930143215

        >>> obj.normalize_date("2025-09-30")
        20250930000000
        """        
        if isinstance(value, (datetime, date)):
            dt = value
        elif isinstance(value, int):
            return value
        
        else:
            try:
                dt = datetime.strptime(value, "%Y-%m-%d")
            except (ValueError, TypeError):
                raise ValueError(f"Non è possibile interpretare {value!r} come data")

        return int(dt.strftime("%Y%m%d%H%M%S"))    
    #--------------------------------------------------------        
    def __init__(self,token:str = "",username:str = "",password:str=""):
        """
        Initialize the client with optional authentication credentials.

        This constructor sets up the base URL for the web service and initializes
        the authentication attributes. It also resets any stored error state.

        Parameters
        ----------
        token : str, optional
            Authentication token. Default is an empty string.
        username : str, optional
            Username for authentication. Default is an empty string.
        password : str, optional
            Password for authentication. Default is an empty string.

        Attributes
        ----------
        base_url : str
            Base URL of the web service API.
        token : str
            Authentication token, if provided.
        id_user : str
            User identifier (initialized as empty).
        email_user : str
            User email (initialized as empty).
        username : str
            Authentication username, if provided.
        password : str
            Authentication password, if provided.
        dbname : str
            Database name (initialized as empty).

        Examples
        --------
        >>> client = MyClient(token="abc123", username="john", password="secret")
        >>> client.base_url
        'https://web.nios4.com/ws/'
        """        
        self.base_url = 'https://web.nios4.com/ws/'
        self.reset_error()
        self.token = token
        self.id_user = ""  
        self.email_user = ""
        self.username = username
        self.password = password
        self.dbname = ""  
    #------------------------------------------------------------
    def login(self, token: str = "") -> bool:
        """
        Authenticate the user and start a session with the web service.

        The function performs login either using username/password or
        an authentication token. If a token is passed, it overrides the
        username/password method. The client state is updated with user
        information and authentication details after a successful login.

        Parameters
        ----------
        token : str, optional
            Authentication token. If provided, it will be used instead of
            username and password. Default is an empty string.

        Returns
        -------
        bool
            True if the login is successful, False otherwise.

        Side Effects
        ------------
        - Updates ``self.token`` if a new token is obtained.
        - Updates ``self.id_user`` and ``self.email_user`` on successful login.
        - Updates ``self.error_code`` and ``self.error_message`` if login fails.

        Raises
        ------
        None directly, but sets error state in attributes if login fails.

        Examples
        --------
        >>> client = MyClient(username="john", password="secret")
        >>> client.login()
        True

        >>> client = MyClient()
        >>> client.login(token="abc123")
        True

        >>> client.login("wrongtoken")
        False
        """
        self.reset_error()

        if token != "":
            self.token = token

        url = self.base_url + f'?action=user_login&email={self.username}&password={self.password}'
        if self.token != "":
            url = self.base_url + f'?action=user_login&token={self.token}'
               
        response= requests.get(url)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return False
            else:
                user = values['user']
                self.id_user = user['id']
                self.email_user = user['email']
                if self.token == "":
                    self.token = user['token']
                return True
        else:
            self.error_code = "E1"
            self.error_message = response.text
            return False
    #------------------------------------------------------------
    def database_list(self, token: str = "") -> Optional[list]:
        """
        Retrieve the list of databases available for the authenticated user.

        The function sends a request to the web service using the current
        authentication token. If a token is passed as argument, it overrides
        the stored token. If no valid token is available, the function sets
        an error state and returns ``None``.

        Parameters
        ----------
        token : str, optional
            Authentication token. If provided, it will be used instead of
            the stored token. Default is an empty string.

        Returns
        -------
        list of dict or None
            A list of databases (as dictionaries) if the request is successful.
            Returns ``None`` if authentication fails, the request fails, or
            an error occurs.

        Side Effects
        ------------
        - Updates ``self.token`` if a new token is provided.
        - Updates ``self.error_code`` and ``self.error_message`` if the request fails.

        Raises
        ------
        None directly, but sets error state in attributes if login fails.

        Examples
        --------
        >>> client = MyClient(token="abc123")
        >>> dbs = client.database_list()
        >>> isinstance(dbs, list)
        True

        >>> client = MyClient()
        >>> client.database_list("wrongtoken")
        None
        """
        self.reset_error()

        if token != "":
            self.token = token
 
        if self.token != "":
            url = self.base_url + f'?action=database_list&token={self.token}'
        else:
            self.error_code = "TK1"
            self.errormessage = "Token missing"
            return None
        
        response= requests.get(url)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values['db']
        else:
            self.error_code = "E2"
            self.error_message = response.text
            return None     
    #------------------------------------------------------------
    def users_list(self,dbname:str="",token:str="") -> Optional[list]:
        """
        Retrieve the list of users for the specified database.

        The function queries the web service to fetch users associated with
        a given database. If a token or database name is provided as arguments,
        they override the stored values. If no valid token is available, the
        function sets an error state and returns ``None``.

        Parameters
        ----------
        dbname : str, optional
            The name of the database to query. If provided, it overrides the
            stored database name. Default is an empty string.
        token : str, optional
            Authentication token. If provided, it overrides the stored token.
            Default is an empty string.

        Returns
        -------
        list of dict or None
            A list of users (as dictionaries) if the request is successful.
            Returns ``None`` if authentication fails, the request fails,
            or an error occurs.

        Side Effects
        ------------
        - Updates ``self.dbname`` if a new database name is provided.
        - Updates ``self.token`` if a new token is provided.
        - Updates ``self.error_code`` and ``self.error_message`` if the request fails.

        Raises
        ------
        None directly, but sets error state in attributes if login fails.

        Examples
        --------
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> users = client.users_list()
        >>> isinstance(users, list)
        True

        >>> client = MyClient()
        >>> client.users_list("mydb", "wrongtoken")
        None
        """
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token

        if self.token != "":
            url = self.base_url + f'?action=users&token={self.token}&db={self.dbname}'
        else:
            self.error_code = "TK1"
            self.error_message = "Token missing"
            return None
        
        response= requests.get(url)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values['users']
        else:
            self.error_code = "E3"
            self.error_message = response.text
            return None     
    #------------------------------------------------------------
    def table_list(self,dbname:str="",token:str="") -> Optional[list]:
        """
        Retrieve the list of tables available in the specified database.

        The function queries the web service to fetch all tables associated
        with a given database. If a token or database name is provided as
        arguments, they override the stored values. If no valid token is
        available, the function sets an error state and returns ``None``.

        Parameters
        ----------
        dbname : str, optional
            The name of the database to query. If provided, it overrides the
            stored database name. Default is an empty string.
        token : str, optional
            Authentication token. If provided, it overrides the stored token.
            Default is an empty string.

        Returns
        -------
        list of dict or None
            A list of tables (as dictionaries) if the request is successful.
            Returns ``None`` if authentication fails, the request fails,
            or an error occurs.

        Side Effects
        ------------
        - Updates ``self.dbname`` if a new database name is provided.
        - Updates ``self.token`` if a new token is provided.
        - Updates ``self.error_code`` and ``self.error_message`` if the request fails.

        Raises
        ------
        None directly, but sets error state in attributes if login fails.

        Examples
        --------
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> tables = client.table_list()
        >>> isinstance(tables, list)
        True

        >>> client = MyClient()
        >>> client.table_list("mydb", "wrongtoken")
        None
        """
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token

        if self.token != "":
            url = self.base_url + f'?action=table_list&token={self.token}&db={self.dbname}'
        else:
            self.error_code = "TK1"
            self.error_message = "Token missing"
            return None
        
        response= requests.get(url)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values['tables']
        else:
            self.error_code = "E4"
            self.error_message = response.text
            return None     
    #------------------------------------------------------------
    def table_info(self,tablename:str,dbname:str="",token:str="") -> Optional[dict]:
        """
        Retrieve detailed information about a specific table.

        The function queries the web service to fetch metadata of a given table,
        including parameters, expressions, and applied styles. If a token or
        database name is provided as arguments, they override the stored values.
        If no valid token is available, the function sets an error state and
        returns ``None``.

        Parameters
        ----------
        tablename : str
            The name of the table to query.
        dbname : str, optional
            The name of the database containing the table. If provided, it
            overrides the stored database name. Default is an empty string.
        token : str, optional
            Authentication token. If provided, it overrides the stored token.
            Default is an empty string.

        Returns
        -------
        dict or None
            A dictionary containing the table's metadata (parameters,
            expressions, styles) if the request is successful.
            Returns ``None`` if authentication fails, the request fails,
            or an error occurs.

        Side Effects
        ------------
        - Updates ``self.dbname`` if a new database name is provided.
        - Updates ``self.token`` if a new token is provided.
        - Updates ``self.error_code`` and ``self.error_message`` if the request fails.

        Raises
        ------
        None directly, but sets error state in attributes if the request fails.

        Examples
        --------
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> info = client.table_info("customers")
        >>> isinstance(info, dict)
        True

        >>> client = MyClient()
        >>> client.table_info("orders", "mydb", "wrongtoken")
        None
        """
        self.reset_error()

        if dbname != "":
            self.dbname = dbname        
        if token != "":
            self.token = token

        if self.token != "":
            url = self.base_url + f'?action=table_info&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.errorcode = "TK1"
            self.errormessage = "Token missing"
            return None
        
        response= requests.get(url)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values['table']
        else:
            self.error_code = "E5"
            self.error_message = response.text
            return None     
    #------------------------------------------------------------
    def fields_info(self,tablename:str,dbname:str="",token:str="") -> Optional[list]:
        """
        Retrieve the fields and their parameters for a specific table.

        The function queries the web service to fetch the fields that compose
        a given table, along with all their parameters and metadata. If a token
        or database name is provided as arguments, they override the stored
        values. If no valid token is available, the function sets an error state
        and returns ``None``.

        Parameters
        ----------
        tablename : str
            The name of the table to query.
        dbname : str, optional
            The name of the database containing the table. If provided, it
            overrides the stored database name. Default is an empty string.
        token : str, optional
            Authentication token. If provided, it overrides the stored token.
            Default is an empty string.

        Returns
        -------
        list of dict or None
            A list of fields (as dictionaries with parameters and metadata)
            if the request is successful. Returns ``None`` if authentication
            fails, the request fails, or an error occurs.

        Side Effects
        ------------
        - Updates ``self.dbname`` if a new database name is provided.
        - Updates ``self.token`` if a new token is provided.
        - Updates ``self.error_code`` and ``self.error_message`` if the request fails.

        Raises
        ------
        None directly, but sets error state in attributes if the request fails.

        Examples
        --------
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> fields = client.fields_info("customers")
        >>> isinstance(fields, list)
        True

        >>> client = MyClient()
        >>> client.fields_info("orders", "mydb", "wrongtoken")
        None
        """
        self.reset_error()

        if dbname != "":
            self.dbname = dbname        
        if token != "":
            self.token = token

        if self.token != "":
            url = self.base_url + f'?action=table_info&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.errorcode = "TK1"
            self.errormessage = "Token missing"
            return None
        
        response= requests.get(url)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values['fields']
        else:
            self.error_code = "E6"
            self.error_message = response.text
            return None     
    #------------------------------------------------------------
    def get_record(self,tablename:str,gguid:str,dbname:str="",token:str="") -> Optional[list]:
        """
        Retrieve a specific record from a table by its unique identifier (gguid).

        The function queries the web service to fetch a single record from
        the specified table using its unique global identifier (gguid).
        If a token or database name is provided as arguments, they override
        the stored values. If no valid token is available, the function sets
        an error state and returns ``None``.

        Parameters
        ----------
        tablename : str
            The name of the table containing the record.
        gguid : str
            The unique global identifier of the record to retrieve.
        dbname : str, optional
            The name of the database containing the table. If provided, it
            overrides the stored database name. Default is an empty string.
        token : str, optional
            Authentication token. If provided, it overrides the stored token.
            Default is an empty string.

        Returns
        -------
        list of dict or None
            The record data as a list of dictionaries if the request is successful.
            Returns ``None`` if authentication fails, the request fails,
            or an error occurs.

        Side Effects
        ------------
        - Updates ``self.dbname`` if a new database name is provided.
        - Updates ``self.token`` if a new token is provided.
        - Updates ``self.error_code`` and ``self.error_message`` if the request fails.

        Raises
        ------
        None directly, but sets error state in attributes if the request fails.

        Examples
        --------
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> record = client.get_record("customers", "gguid-12345")
        >>> isinstance(record, list)
        True

        >>> client = MyClient()
        >>> client.get_record("orders", "gguid-00000", "mydb", "wrongtoken")
        None
        """
        self.reset_error()
        if dbname != "":
            self.dbname = dbname        
        if token != "":
            self.token = token
        if self.token != "":
            url = self.base_url + f'?action=model&token={self.token}&db={self.dbname}&tablename={tablename}&gguid={gguid}'
        else:
            self.error_code = "TK1"
            self.error_message = "Token missing"
            return None
        response= requests.get(url)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values['records']
        else:
            self.error_code = "E7"
            self.error_message = response.text
            return None
    #------------------------------------------------------------
    def detail_delete(self,tablename:str,gguid:str,dbname:str ="",token:str="")-> Optional[dict]:
        """
        Delete a specific record and its related details from a table.

        The function sends a request to the web service to delete a record
        identified by its unique global identifier (gguid) from the specified
        table. Related data in linked tables is also removed. If a token or
        database name is provided as arguments, they override the stored values.
        If no valid token is available, the function sets an error state and
        returns ``None``.

        Parameters
        ----------
        tablename : str
            The name of the table from which to delete the record.
        gguid : str
            The unique global identifier of the record to delete.
        dbname : str, optional
            The name of the database containing the table. If provided, it
            overrides the stored database name. Default is an empty string.
        token : str, optional
            Authentication token. If provided, it overrides the stored token.
            Default is an empty string.

        Returns
        -------
        dict or None
            A dictionary with the deletion result if successful.
            Returns ``None`` if authentication fails, the request fails,
            or an error occurs.

        Side Effects
        ------------
        - Updates ``self.dbname`` if a new database name is provided.
        - Updates ``self.token`` if a new token is provided.
        - Updates ``self.error_code`` and ``self.error_message`` if the request fails.

        Raises
        ------
        None directly, but sets error state in attributes if the request fails.

        Examples
        --------
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> result = client.detail_delete("customers", "gguid-12345")
        >>> isinstance(result, dict)
        True

        >>> client = MyClient()
        >>> client.detail_delete("orders", "gguid-00000", "mydb", "wrongtoken")
        None
        """
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
            self.error_code = "TK1"
            self.error_message = "Token missing"
            return None
        response= requests.post(url, json=payload)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values
        else:
            self.error_code = "E8"
            self.error_message = response.text
            return None   
    #------------------------------------------------------------
    def detail_resolve(self,tablename:str,gguid:str,dbname:str ="",token:str=""):
        """
        Force the server to recalculate a record and its related data.

        The function sends a request to the web service to trigger a recalculation
        of a specific record. This process executes all expressions defined in the
        table and related tables, and also recalculates any value distributors.
        If a token or database name is provided as arguments, they override the
        stored values. If no valid token is available, the function sets an error
        state and returns ``None``.

        Parameters
        ----------
        tablename : str
            The name of the table containing the record.
        gguid : str
            The unique global identifier of the record to recalculate.
        dbname : str, optional
            The name of the database containing the table. If provided, it
            overrides the stored database name. Default is an empty string.
        token : str, optional
            Authentication token. If provided, it overrides the stored token.
            Default is an empty string.

        Returns
        -------
        dict or None
            A dictionary with the recalculation result if successful.
            Returns ``None`` if authentication fails, the request fails,
            or an error occurs.

        Side Effects
        ------------
        - Updates ``self.dbname`` if a new database name is provided.
        - Updates ``self.token`` if a new token is provided.
        - Updates ``self.error_code`` and ``self.error_message`` if the request fails.

        Raises
        ------
        None directly, but sets error state in attributes if the request fails.

        Examples
        --------
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> result = client.detail_resolve("orders", "gguid-98765")
        >>> isinstance(result, dict)
        True

        >>> client = MyClient()
        >>> client.detail_resolve("orders", "gguid-00000", "mydb", "wrongtoken")
        None
        """        
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
            self.error_code = "TK1"
            self.error_message = "Token missing"
            return None
        response= requests.post(url, json=payload)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values
        else:
            self.error_code = "E9"
            self.error_message = response.text
            return None   

    #------------------------------------------------------------
    def fuzzy_records(self,tablename:str,fields_search: List[str],fields_return: List[str],
                      query:str,dbname:str ="",token:str="",threshold:Decimal=0.5,
                      search_by:Dict[str, Any] | None = None,
                      conditions:Dict[str, Any] | None = None,
                      iduser:str = "")-> Optional[list]:
        """
        Perform a fuzzy semantic search on records in a table.

        The function sends a request to the ``model_fuzzy`` API endpoint, which
        searches for records in the specified table matching a query string
        against one or more fields using fuzzy matching. Additional filters
        such as field conditions, search criteria, and user-specific filters
        can be applied.

        Parameters
        ----------
        tablename : str
            The name of the table to query.
        fields_search : list of str
            The list of fields to apply the fuzzy search on.
        fields_return : list of str
            The list of fields to return in the result. If empty, all fields
            are returned by default.
        query : str
            The string to search for in the specified fields.
        dbname : str, optional
            The name of the database containing the table. Overrides the stored
            database name if provided. Default is an empty string.
        token : str, optional
            Authentication token. Overrides the stored token if provided.
            Default is an empty string.
        threshold : Decimal, optional
            Minimum match threshold for fuzzy search, between 0.0 and 1.0.
            Default is 0.5. A value of 0.0 matches everything, while 1.0
            requires an exact match.
        search_by : dict of {str: Any}, optional
            Dictionary of field/value pairs to filter records with ``LIKE`` in
            logical AND.
        conditions : dict of {str: Any}, optional
            Dictionary of field/value pairs to filter records with equality in
            logical AND.
        iduser : str, optional
            User ID (UTA) to filter results by user-specific access. Default is
            an empty string.

        Returns
        -------
        list of dict or None
            A list of matching records as dictionaries if the request succeeds.
            Returns ``None`` if authentication fails, the request fails,
            or an error occurs.

        Side Effects
        ------------
        - Updates ``self.dbname`` if a new database name is provided.
        - Updates ``self.token`` if a new token is provided.
        - Updates ``self.error_code`` and ``self.error_message`` if the request fails.

        Raises
        ------
        None directly, but sets error state in attributes if the request fails.

        Examples
        --------
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> results = client.fuzzy_records(
        ...     tablename="customers",
        ...     fields_search=["name", "surname"],
        ...     fields_return=["id", "name", "surname", "email"],
        ...     query="Jon",
        ...     threshold=0.7
        ... )
        >>> isinstance(results, list)
        True

        >>> client.fuzzy_records("orders", ["description"], ["id", "description"], "laptop", "mydb", "wrongtoken")
        None
        """
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
        if search_by:
            payload['search_by'] = search_by
        if conditions:
            payload['conditions'] = conditions
        if iduser != "":
            payload['uta'] = iduser

        url = ""
        if self.token != "":
            url = self.base_url + f'?action=model_fuzzy&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.error_code = "TK1"
            self.error_message = "Token missing"
            return None

        response= requests.post(url, json=payload)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values['results']
        else:
            self.error_code = "E10"
            self.error_message = response.text
            return None   
    #------------------------------------------------------------
    def find_records(self,tablename:str,dbname:str="",token:str="",fields_search: List[str] = None,value_search: str = "",
                    search_by:Dict[str, Any] | None = None,
                    conditions:Dict[str, Any] | None = None,order_info:List[Any]= None,
                    iduser:str = "")-> Optional[list]:
        """
        Query records from a table with textual search, filters, and ordering.

        This function calls the ``model`` endpoint to read records from a table,
        applying (optionally) a text search over one or more fields, additional
        LIKE/equality filters, ordering, and user-based filtering (UTA). Results
        are subject to the user's permissions.

        Parameters
        ----------
        tablename : str
            Name of the table to read.
        dbname : str, optional
            Database name. If provided, overrides the stored value. Default ``""``.
        token : str, optional
            Authentication token. If provided, overrides the stored value. Default ``""``.
        fields_search : list of str, optional
            Fields to apply the textual search on (body ``search.fields``). If omitted
            or empty, no textual search clause is added.
        value_search : str, optional
            Query string to search within ``fields_search`` (body ``search.query``).
            Effective only if both ``fields_search`` and ``value_search`` are provided.
            Default ``""``.
        search_by : dict of {str: Any}, optional
            Field/value pairs filtered with ``LIKE`` in logical AND (body ``search_by``).
        conditions : dict of {str: Any}, optional
            Field/value pairs filtered with equality in logical AND (body ``conditions``).
            Values can be a scalar (matched as string) or an array of scalars (matched
            with SQL ``IN`` semantics).
        order_info : list, optional
            Ordering specification (body ``order_info``) as
            ``[["field_name", True_for_ASC], ...]``. Example: ``[["name", True], ["id", False]]``.
        iduser : str, optional
            Single user ID to filter by UTA (body ``uta``). Default ``""``.

        Returns
        -------
        list of dict or None
            The list of records (``records``) if the request is successful.
            Returns ``None`` if authentication fails, the request fails, or an error occurs.

        Notes
        -----
        - Additional optional capabilities of the ``model`` endpoint (not used here)
        include: pagination (``page``, ``perpage``), specific record by ``gguid``,
        time-range filters for calendars (``timerange``), multi-``gguids`` filter,
        grouping (``group_by``), and summary totals (``totals``).
        - The server response may also include ``total`` (for pagination) and ``totals``
        if requested; this function returns only ``records``.

        Side Effects
        ------------
        - Updates ``self.dbname`` and/or ``self.token`` if provided.
        - Updates ``self.error_code`` and ``self.error_message`` on failure.

        Examples
        --------
        Basic text search on two fields:
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> rows = client.find_records(
        ...     tablename="customers",
        ...     fields_search=["name", "surname"],
        ...     value_search="jon"
        ... )
        >>> isinstance(rows, list)
        True

        Filters with LIKE and equality, plus ordering:
        >>> rows = client.find_records(
        ...     tablename="orders",
        ...     search_by={"customer_name": "doe"},
        ...     conditions={"status": ["open", "pending"]},
        ...     order_info=[["created_at", True]]
        ... )
        >>> rows is None or isinstance(rows, list)
        True
        """
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token
        
        payload = {}
        if fields_search != None and value_search != "":
            payload["search"] = {
                "fields": fields_search,
                "query": value_search
            }
        if search_by:
            payload['search_by'] = search_by
        if conditions:
            payload['conditions'] = conditions
        if order_info:
            payload['order_info'] = order_info
        if iduser != "":
            payload['uta'] = iduser        

        url = ""
        if self.token != "":
            url = self.base_url + f'?action=model&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.error_code = "TK1"
            self.error_message = "Token missing"
            return None

        response= requests.post(url, json=payload)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values['records']
        else:
            self.error_code = "E11"
            self.error_message = response.text
            return None        
    #------------------------------------------------------------
    def save_record(self,tablename: str,values: Dict[str, Any],dbname: str ="",token:str="",is_new:bool=True,delete:bool=False)-> Optional[dict]:
        """
        Save or delete a record in a table.

        This function calls the ``detail_save`` endpoint to persist a record
        in the specified table. Depending on the flags, it can save a new record,
        update an existing one, or delete a record entirely (including related data
        in linked subtables). A valid ``gguid`` must always be provided in
        ``values``.

        Parameters
        ----------
        tablename : str
            Name of the table where the record belongs.
        values : dict
            Dictionary containing the record values. Must include a non-empty
            ``gguid`` key.
        dbname : str, optional
            Database name. If provided, overrides the stored value. Default ``""``.
        token : str, optional
            Authentication token. If provided, overrides the stored value. Default ``""``.
        is_new : bool, optional
            Whether the record is new (``True``) or an update to an existing record (``False``).
            Default is ``True``.
        delete : bool, optional
            If ``True``, the record is deleted instead of saved. Default is ``False``.

        Returns
        -------
        dict or None
            The server response containing the updated record values if successful.
            This may include auto-assigned fields such as ``ind`` (record index),
            counters, or timestamps. Returns ``None`` if the request fails or an
            error occurs.

        Side Effects
        ------------
        - Updates ``self.dbname`` and/or ``self.token`` if provided.
        - Updates ``self.error_code`` and ``self.error_message`` on failure.

        Raises
        ------
        None directly, but sets error state in attributes if:
        - ``values`` does not include a valid ``gguid``.
        - Authentication or permissions fail.
        - The server reports an error.

        Examples
        --------
        Save a new record:
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> record = {"gguid": "gguid-12345", "name": "Alice"}
        >>> result = client.save_record("customers", record, is_new=True)
        >>> isinstance(result, dict)
        True

        Update an existing record:
        >>> record = {"gguid": "gguid-12345", "name": "Alice Updated"}
        >>> result = client.save_record("customers", record, is_new=False)

        Delete a record:
        >>> record = {"gguid": "gguid-12345"}
        >>> result = client.save_record("customers", record, delete=True)
        """
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token
        
        if values["gguid"] == "" or values["gguid"] == None:
            self.error_code = "E1" 
            self.error_message = "Non è definito il gguid del record"
            return None
        
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
            self.error_code = "TK1"
            self.error_message = "Token missing"
            return None
        response= requests.post(url, json=payload)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values
    #------------------------------------------------------------
    def save_records(self,tablename: str,values: List[Dict[str, Any]],dbname: str ="",token:str="") -> Optional[dict]:
        """
        Save multiple records in a table.

        This function calls the ``table_save`` endpoint to persist multiple
        rows in the specified table. Each record must include a valid ``gguid``.
        The function supports inserting or updating records; deletions are
        possible by specifying the ``delete`` field in the payload (not
        currently exposed in this wrapper).

        Parameters
        ----------
        tablename : str
            Name of the table where the records belong.
        values : list of dict
            A list of dictionaries representing the records to save.
            Each dictionary must include a non-empty ``gguid``.
        dbname : str, optional
            Database name. If provided, overrides the stored value.
            Default is ``""``.
        token : str, optional
            Authentication token. If provided, overrides the stored value.
            Default is ``""``.

        Returns
        -------
        dict or None
            The server response containing the saved records if successful.
            Returns ``None`` if authentication fails, the request fails,
            or an error occurs.

        Side Effects
        ------------
        - Updates ``self.dbname`` and/or ``self.token`` if provided.
        - Updates ``self.error_code`` and ``self.error_message`` on failure.

        Raises
        ------
        None directly, but sets error state in attributes if:
        - Any record does not include a valid ``gguid``.
        - Authentication or permissions fail.
        - The server reports an error.

        Examples
        --------
        Save multiple records:
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> rows = [
        ...     {"gguid": "gguid-1", "name": "Alice"},
        ...     {"gguid": "gguid-2", "name": "Bob"}
        ... ]
        >>> result = client.save_records("customers", rows)
        >>> isinstance(result, dict)
        True

        Attempt to save without gguid:
        >>> rows = [{"gguid": "", "name": "Invalid"}]
        >>> result = client.save_records("customers", rows)
        None
        """
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
        payload = {
            "rows": values
        }
        url = ""
        if self.token != "":
            url = self.base_url + f'?action=table_save&token={self.token}&db={self.dbname}&tablename={tablename}'
        else:
            self.error_code = "TK1"
            self.error_message = "Token missing"
            return None
        response= requests.post(url, json=payload)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values
    #------------------------------------------------------------
    def create_data_file(self,filename:str,gguidrif:str="") -> tuple[str, str]:
        """
        Create the JSON payload for saving file metadata.

        This function prepares the data structure needed to register a file
        in the system. It normalizes the file name (removing any directory path),
        ensures a unique identifier (``gguidfile``) is set, and returns both
        the identifier and the serialized JSON body.

        Parameters
        ----------
        filename : str
            The full path or name of the file. The path will be stripped and only
            the base filename will be used.
        gguidrif : str, optional
            The unique identifier for the file. If not provided, a new UUID
            will be generated. Default is an empty string.

        Returns
        -------
        tuple of (str, str)
            A tuple containing:
            - ``gguidfile`` (str): The file's unique identifier.
            - ``body`` (str): The JSON string with the file metadata, including
            ``gguidfile`` and ``nomefile``.

        Examples
        --------
        Generate a payload for a new file:
        >>> gguid, body = client.create_data_file("C:/docs/report.pdf")
        >>> gguid
        '550e8400-e29b-41d4-a716-446655440000'
        >>> body
        '{"gguidfile": "550e8400-e29b-41d4-a716-446655440000", "nomefile": "report.pdf"}'

        Use an existing gguid:
        >>> gguid, body = client.create_data_file("image.png", gguidrif="custom-123")
        >>> gguid
        'custom-123'
        >>> body
        '{"gguidfile": "custom-123", "nomefile": "image.png"}'
        """
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
        """
        Download a file from the server and save it locally.

        This function calls the ``file_download`` endpoint to retrieve the content
        of a file associated with a record (e.g., FILE or IMAGE fields) and writes
        it to the specified local path. The server returns the raw file content,
        not JSON.

        Parameters
        ----------
        path : str
            Local path where the downloaded file will be saved.
        gguidrif : str
            The unique identifier (gguid) of the file to download.
        tablename : str
            The name of the table containing the file reference.
        dbname : str, optional
            The name of the database containing the table. If provided, it overrides
            the stored value. Default is ``""``.
        token : str, optional
            Authentication token. If provided, it overrides the stored value.
            Default is ``""``.

        Returns
        -------
        bool
            ``True`` if the file was downloaded and saved successfully,
            ``False`` otherwise.

        Side Effects
        ------------
        - Updates ``self.dbname`` and/or ``self.token`` if provided.
        - Updates ``self.error_code`` and ``self.error_message`` on failure.
        - Writes the file to disk at the specified ``path``.

        Raises
        ------
        None directly, but sets error state in attributes if:
        - Token is missing.
        - The request fails (HTTP errors, connection issues).
        - The file cannot be saved.

        Notes
        -----
        The endpoint also supports optional parameters not used here:
        - ``thumb``: if set to 1, downloads the image thumbnail.
        - ``filename``: optional name to assign to the downloaded file.
        - ``exiftran``: if set to 1, applies lossless EXIF-based rotation.

        Examples
        --------
        Download a file and save it locally:
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> success = client.download_file("report.pdf", "gguid-12345", "documents")
        >>> success
        True

        Attempt without token:
        >>> client = MyClient()
        >>> success = client.download_file("output.png", "gguid-67890", "images")
        >>> success
        False
        """
        self.reset_error()
        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token        

        url = ""
        if self.token != "":
            url = f'https://app.pocketsell.com/_sync/?action=file_download&token={self.token}&db={self.dbname}&tablename={tablename}&gguid={gguidrif}'
        else:
            self.error_code = "TK1"
            self.error_message = "Token missing"
            return False
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
            return False
        except ValueError:
            # JSON non valido
            print(f"Response non-JSON: {response.text[:500]}")
            return False
        return True        

    #------------------------------------------------------------
    def upload_file(self,path:str,is_image:bool,gguidrif:str,tablename:str, dbname: str ="",token:str="") -> bool:
        """
        Upload a file to the server.

        This function calls the ``file_upload`` endpoint to send a file to the
        synchronizer. The file can be associated with a record field of type
        FILE or IMAGE. If a file with the same GGUID already exists, it will be
        overwritten on the server.

        Parameters
        ----------
        path : str
            Local path of the file to upload.
        is_image : bool
            Whether the file is an image. If ``True``, the server will attempt
            to generate a thumbnail. If ``False``, the file is treated as a generic file.
        gguidrif : str
            The unique identifier (gguid) of the file, generated by the client.
        tablename : str
            The name of the table containing the file reference.
        dbname : str, optional
            The name of the database containing the table. If provided, it
            overrides the stored value. Default is ``""``.
        token : str, optional
            Authentication token. If provided, it overrides the stored value.
            Default is ``""``.

        Returns
        -------
        bool
            ``True`` if the file was uploaded successfully, ``False`` otherwise.

        Side Effects
        ------------
        - Updates ``self.dbname`` and/or ``self.token`` if provided.
        - Updates ``self.error_code`` and ``self.error_message`` on failure.
        - Sends the file contents to the server over HTTP.

        Raises
        ------
        None directly, but sets error state in attributes if:
        - Token is missing.
        - The request fails (HTTP errors, connection issues).
        - The server rejects the file.

        Notes
        -----
        According to the API:
        - The request body is sent as multipart form data with keys:
        ``gguid_X``, ``file_X``, ``type_X``, and optional ``args_X``.
        - If ``type_X`` is ``image``, the synchronizer may create a thumbnail.
        - If the file already exists with the same GGUID, it will be overwritten.
        - Error ``limit_reached`` indicates the database has reached its file limit.

        Examples
        --------
        Upload an image:
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> success = client.upload_file("photo.png", is_image=True, gguidrif="gguid-123", tablename="images")
        >>> success
        True

        Upload a generic file:
        >>> success = client.upload_file("document.pdf", is_image=False, gguidrif="gguid-456", tablename="files")
        >>> success
        True
        """
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
            self.error_code = "TK1"
            self.error_message = "Token missing"
            return False

        try:
            resp = requests.post(url, data=data, headers={"Content-Type": "application/octet-stream"}, timeout=30)
            resp.raise_for_status()

            valori = resp.json()
            return valori.get("result") != "KO"
        except requests.RequestException as e:
            self.error_code = "F1"
            self.error_message = str(e)
            print(f"HTTP error: {e}")
            return False
        except ValueError:
            # JSON non valido
            print(f"Response non-JSON: {resp.text[:500]}")
            return False
        return True
        
    #------------------------------------------------------------
    def sync(self,dbname: str ="",token:str=""):
        """
        Force synchronization of the database with the Syncone server.

        This function calls the ``sync`` endpoint to synchronize the local
        database with the remote server. Synchronization may be full or
        partial, depending on server response. The function returns the
        synchronization metadata provided by the server.

        Parameters
        ----------
        dbname : str, optional
            Name of the database to synchronize. If provided, overrides the stored
            value. Default is ``""``.
        token : str, optional
            Authentication token. If provided, overrides the stored value.
            Default is ``""``.

        Returns
        -------
        dict or None
            A dictionary containing synchronization metadata if successful:
            - ``sync`` (dict):
                - ``partial`` (bool): Whether partial synchronization is required.
                - ``partial_from`` (int): The next index to use for continuing partial sync (if ``partial`` is True).
                - ``partial_total`` (int): Total number of records expected in the partial sync (if ``partial`` is True).
            - ``sync_last_tid`` (int): TID of the last completed synchronization.
            - ``sync_first`` (bool): Whether this was the first synchronization.
            Returns ``None`` if authentication fails, the request fails, or an error occurs.

        Side Effects
        ------------
        - Updates ``self.dbname`` and/or ``self.token`` if provided.
        - Updates ``self.error_code`` and ``self.error_message`` on failure.

        Raises
        ------
        None directly, but sets error state in attributes if:
        - Token is missing.
        - The request fails (HTTP errors, connection issues).
        - The server reports an error.

        Examples
        --------
        Full sync:
        >>> client = MyClient(token="abc123", dbname="mydb")
        >>> result = client.sync()
        >>> isinstance(result, dict)
        True

        Handling partial sync:
        >>> sync_info = client.sync("mydb", "abc123")
        >>> if sync_info and sync_info["sync"].get("partial"):
        ...     print("Partial sync, continue from:", sync_info["sync"]["partial_from"])
        """
        self.reset_error()

        if dbname != "":
            self.dbname = dbname
        if token != "":
            self.token = token

        if self.token != "":
            url = self.base_url + f'?action=sync&token={self.token}&db={self.dbname}'
        else:
            self.error_code = "TK1"
            self.error_message = "Token missing"
            return None
        response= requests.get(url)
        if response.status_code == 200:
            values= response.json()
            if values["error"] == True:
                self.error_code = values["error_code"]
                self.error_message = values["error_message"]
                return None
            else:
                return values

