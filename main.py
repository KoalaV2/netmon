#!/usr/bin/env python3
import requests
import json
from dotenv import load_dotenv
import os
import mariadb

load_dotenv()

PI_IP = os.getenv("PI_IP")
API_KEY = os.getenv("API_KEY")
DB_USER = os.getenv("DB_USER")
DB_PASSWD = os.getenv("DB_PASSWD")
DB_IP = os.getenv("DB_IP")
DB_DATABASE = os.getenv("DB_DATABASE")


try:
    conn = mariadb.connect(
        user=DB_USER,
        password=DB_PASSWD,
        host=DB_IP,
        port=3306,
        database=DB_DATABASE

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    exit()

def scannet():
    c = conn.cursor()
    print("[*] Creating table if it doesn't exist...")
    c.execute('''CREATE TABLE IF NOT EXISTS network (addres VARCHAR(255),name VARCHAR(255),macaddr VARCHAR(255),maccompany VARCHAR(255));''')
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Sec-GPC': '1',
        'DNT': '1',
    }

    params = (
        ('auth', API_KEY),
        ('network', ''),
        ('_', '1624463201689'),
    )

    response = requests.get(f'http://{PI_IP}/admin/api_db.php', headers=headers,params=params)
    print("[*] Sending request...")
    devices = response.text
    json_data = json.loads(devices)
    json_data = json_data['network']
    print("[*] Sending data to database...")
    for entry in json_data:
        host = None
        hostname = None
        macaddr = None
        maccompany = None
        if entry['ip']:
            host = entry['ip'][0]
        if entry['name']:
            hostname = entry['name'][0]
        if entry['hwaddr']:
            macaddr = entry['hwaddr']
        if entry['macVendor']:
            maccompany = entry['macVendor']
        c.execute("insert into network values (?,?,?,?);", (host,hostname,macaddr,maccompany))
        conn.commit()
    print("[*] Network scan has completed and has been uploaded...")

def client():
    cur = conn.cursor()
    cur.execute('SELECT distinct * from network;')
    print("[*] Fetching results from database...")
    for entry in cur:
        host = None
        hostname = None
        macaddr = None
        maccompany = None
        if entry[0]:
            host = entry[0]
        if entry[1]:
            hostname = entry[1]
        if entry[2]:
            macaddr = entry[2]
        if entry[3]:
            maccompany = entry[3]
    conn.close()

def main():
    #scannet()
    client()


if __name__ == "__main__":
    main()
