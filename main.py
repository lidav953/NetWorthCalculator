import base64
import os
import datetime
import plaid
import json
import time
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from config import *
import sqlite3
import server
from werkzeug.exceptions import abort

client = plaid.Client(client_id=PLAID_CLIENT_ID,
                      secret=PLAID_SECRET,
                      environment=PLAID_ENV,
                      api_version='2019-05-29')

def get_db_connection():
  conn = sqlite3.connect('database.db')
  conn.row_factory = sqlite3.Row
  return conn

def get_accounts():
    conn = get_db_connection()
    accounts = conn.execute('SELECT * FROM accounts').fetchall()
    conn.close()
    return accounts

def get_account(account_id):
    conn = get_db_connection()
    account = conn.execute('SELECT * FROM accounts WHERE id = ?', 
                            (account_id,)).fetchone()
    conn.close()
    if account is None:
        abort(404)
    return account

def calculate_net_worth(accounts):
    total = 0
    for account in accounts:
        total += account['balance']
    return total

def update_balances(accounts):
    conn = get_db_connection()
    auth_keys = conn.execute('SELECT DISTINCT auth_key FROM accounts').fetchall()
    for auth_key in auth_keys:
        #print(auth_key)
        #print(type(auth_key))
        balance_response = client.Accounts.balance.get(auth_key)
        for account in balance_response['accounts']:
            name = account['name']
            nickname = ''
            if account['official_name'] is not None:
                nickname = account['official_name']
            balance = account['balances']['current']
            if account['type'] == 'credit':
                balance = (-1)*balance

            #Update the existing account with the balance info
            conn.execute('UPDATE accounts SET balance = ?, auth_key = ? WHERE account_name = ? AND account_nickname = ?',
                        (balance, auth_key, name, nickname))
            print('Updated account {} {} to {} balance.'.format(name, nickname, balance))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    accounts = get_accounts()
    #update_balances(accounts)
    net_worth = calculate_net_worth(accounts)
    print('Net Worth is: {}'.format(net_worth))