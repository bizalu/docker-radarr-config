import requests
import os.path
import time
import sys
import json
import sqlite3
import traceback
import xml.etree.ElementTree as ET

CONFIG_FILE = 'config.xml'
RADARR_URL = 'https://radarr-dev.apps.ovv.elserverido.com'
RADARR_DB = '/config/radarr.db'

RADARR_USER = "admin"
RADARR_PASSWORD = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
RADARR_ROOTPATH = "/movies/films"
RADARR_REMOTEPATH = "/downloads/"
RADARR_LOCALPATH = "/movies/downloads/"

INDEXER_NAME = "Jackett"
INDEXER_URL = "http://jackett-web:9117/api/v2.0/indexers/yggtorrent/results/torznab/"
INDEXER_APIKEY = "6ktsn66wjqri8766jtmuhe944p168p1o"

DOWNLOADER_NAME = "Transmission"
DOWNLOADER_URL = "transmission-web"
DOWNLOADER_PORT = 9091
DOWNLOADER_USER = "admin"
DOWNLOADER_PASSWORD = "x4L9JvRu9wT4"
DOWNLOADER_CATEGORY = "films"



def get_apikey(file):
    apikey = ""

    if os.path.isfile(file) and os.path.exists(file):
        tree = ET.parse(file)
        root = tree.getroot()

        apikey = root.find("ApiKey").text

    return apikey

def set_authenticationmethod(file, method):
    if os.path.isfile(file) and os.path.exists(file):
        tree = ET.parse(file)
        root = tree.getroot()

        root.find("AuthenticationMethod").text = method
        tree.write(file)

def check_health(url, apikey):
    api_url = url + "/api/v3/health"
    api_header = {'accept': 'application/json', 'X-Api-Key': apikey}

    try:
        response = requests.get(api_url, headers=api_header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print(errh)
        sys.exit(response.status_code)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)

    return response.status_code


def set_credential(database, username, password):
    #Create user in database
    data = ('652bf21b-fe69-47f7-8e52-80e0572a9025', username, password)
    query = "INSERT INTO Users (Identifier,Username,Password) VALUES(?, ?, ?)"
    connexion = sqlite3(database)
    db = connexion.cursor()

    try:
        db.execute(query, data)
        connexion.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    db.close()



def add_rootfolder(url, apikey, folder):
    api_url = url + "/api/v3/rootfolder"
    api_header = {'accept': 'application/json', 'X-Api-Key': apikey, 'Content-Type': 'application/json'}
    api_data = {
        'path': folder
    }

    try:
        response = requests.post(api_url, headers=api_header, json=api_data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        message = json.loads(json.dumps(response.json()[0]))
        if message["errorMessage"] == "Path is already configured as a root folder":
            print("*** warning *** root folder %s already exist" % folder)
        else:
            print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)

    return response.status_code


def add_torznab_indexer(url, apikey, name, indexer_url, indexer_apikey):
    api_url = url + "/api/v3/indexer"
    api_header = {'accept': 'application/json', 'X-Api-Key': apikey, 'Content-Type': 'application/json'}
    api_data = {
        "name": name,
        "fields": [
            {
                "order": 0,
                "name": "baseUrl",
                "label": "URL",
                "value": indexer_url,
                "type": "textbox"
            },
            {
                "order": 3,
                "name": "apiKey",
                "label": "API Key",
                "value": indexer_apikey,
                "type": "textbox"
            },
            {
                "order": 4,
                "name": "categories",
                "label": "Categories",
                "helpText": "Drop down list; at least one category must be selected.",
                "value": [
                    2000,
                    5000
                ],
                "type": "select",
                "selectOptionsProviderAction": "newznabCategories"
            }
        ],
        "implementationName": "Torznab",
        "implementation": "Torznab",
        "configContract": "TorznabSettings",
        "enableRss": True,
        "enableAutomaticSearch": True,
        "enableInteractiveSearch": True,
        "priority": 25
    }

    try:
        response = requests.post(api_url, headers=api_header, json=api_data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        message = json.loads(json.dumps(response.json()[0]))
        if message["errorMessage"] == "Should be unique":
            print("*** warning *** indexer %s already exist" % name)
        else:
            print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)

    return response.status_code


def add_transmission_downloader(url, apikey, name, downloader_url, downloader_port, downloader_username,
                                downloader_password, downloader_category):
    api_url = url + "/api/v3/downloadclient"
    api_header = {'accept': 'application/json', 'X-Api-Key': apikey, 'Content-Type': 'application/json'}
    api_data = {
        "enable": True,
        "name": name,
        "fields": [
            {
                "order": 0,
                "name": "host",
                "label": "Host",
                "value": downloader_url,
                "type": "textbox",
                "advanced": False
            },
            {
                "order": 1,
                "name": "port",
                "label": "Port",
                "value": downloader_port,
                "type": "textbox",
                "advanced": False
            },
            {
                "order": 4,
                "name": "username",
                "label": "Username",
                "value": downloader_username,
                "type": "textbox",
                "advanced": False
            },
            {
                "order": 5,
                "name": "password",
                "label": "Password",
                "value": downloader_password,
                "type": "password",
                "advanced": False
            },
            {
                "order": 6,
                "name": "movieCategory",
                "label": "Category",
                "helpText": "Adding a category specific to Radarr avoids conflicts with unrelated non-Radarr "
                            "downloads. Using a category is optional, but strongly recommended. Creates a [category] "
                            "subdirectory in the output directory.",
                "value": downloader_category,
                "type": "textbox",
                "advanced": False
            }
        ],
        "implementationName": "Transmission",
        "implementation": "Transmission",
        "configContract": "TransmissionSettings",
        "removeCompletedDownloads": True,
        "removeFailedDownloads": True
    }

    try:
        response = requests.post(api_url, headers=api_header, json=api_data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        message = json.loads(json.dumps(response.json()[0]))
        if message["errorMessage"] == "Should be unique":
            print("*** warning *** downloader client %s already exist" % name)
        else:
            print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)

    return response.status_code


def add_downloader_remotepath(url, apikey, downloader_url, remote_path, local_path):
    api_url = url + "/api/v3/remotepathmapping"
    api_header = {'accept': 'application/json', 'X-Api-Key': apikey, 'Content-Type': 'application/json'}
    api_data = {
        "host": downloader_url,
        "remotePath": remote_path,
        "localPath": local_path
    }

    try:
        response = requests.post(api_url, headers=api_header, json=api_data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        message = json.loads(json.dumps(response.json()))
        if message["message"] == "RemotePath already mounted.":
            print("*** warning *** downloader remote path for %s already exist" % downloader_url)
        else:
            print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)

    return response.status_code


print("[INIT] Waiting for application %s ..." % RADARR_URL)
RADARR_APIKEY = get_apikey(CONFIG_FILE)
while check_health(RADARR_URL, RADARR_APIKEY) != 200:
    time.sleep(1)

print("[INIT] Set Credential to application ...")
#set_credential(RADARR_DB, RADARR_USER, RADARR_PASSWORD)
set_authenticationmethod(CONFIG_FILE, "forms")

print("[INIT] Configuring root path...")
add_rootfolder(RADARR_URL, RADARR_APIKEY, RADARR_ROOTPATH)

print("[INIT] Configuring Indexer...")
add_torznab_indexer(RADARR_URL, RADARR_APIKEY, INDEXER_NAME, INDEXER_URL, INDEXER_APIKEY)

print("[INIT] Configuring Downloader Client...")
add_transmission_downloader(RADARR_URL, RADARR_APIKEY, DOWNLOADER_NAME, DOWNLOADER_URL, DOWNLOADER_PORT, DOWNLOADER_USER,
                            DOWNLOADER_PASSWORD, DOWNLOADER_CATEGORY)
add_downloader_remotepath(RADARR_URL, RADARR_APIKEY, DOWNLOADER_URL, RADARR_REMOTEPATH, RADARR_LOCALPATH)