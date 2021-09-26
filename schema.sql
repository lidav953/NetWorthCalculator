DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_name TEXT NOT NULL,
    account_nickname TEXT NOT NULL,
    account_type TEXT NOT NULL,
    balance INTEGER,
    auth_key TEXT NOT NULL
);