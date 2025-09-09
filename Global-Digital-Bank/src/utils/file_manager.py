import csv
from src.models.account import Account
from datetime import datetime

ACCOUNT_FILE = "/Users/harshahs/Desktop/global_digital_bank/Global-Digital_Bank/Global-Digital-Bank/Global-Digital-Bank/data/accounts.csv"
# Preserve existing transactions.log usage, but add split logs for role-based logging
USER_TRANSACTIONS_FILE = "/Users/harshahs/Desktop/global_digital_bank/Global-Digital_Bank/Global-Digital-Bank/Global-Digital-Bank/data/user_transactions.log"
ADMIN_ACTIONS_FILE = "/Users/harshahs/Desktop/global_digital_bank/Global-Digital_Bank/Global-Digital-Bank/Global-Digital-Bank/data/admin_actions.log"
TRANSACTIONS_FILE = "/Users/harshahs/Desktop/global_digital_bank/Global-Digital_Bank/Global-Digital-Bank/Global-Digital-Bank/data/transactions.log"

def save_accounts(accounts):
    with open(ACCOUNT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["account_number", "name", "age", "balance", "account_type", "status", "time","pin"])
        for acc in accounts.values():
            d = acc.to_dict()
            writer.writerow(
                [
                    d["account_number"],
                    d["name"],
                    d["age"],
                    d["balance"],
                    d["account_type"],
                    d["status"],
                    d['timestamp'],
                    d["pin"]
                    ])


def load_accounts():
    accounts = {}
    try:
        with open(ACCOUNT_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                acc = Account(
                    account_number=row["account_number"],
                    name= row["name"],
                    age=row["age"],
                    account_type=row["account_type"],
                    balance=row["balance"],
                    status=row["status"],
                    timestamp=row["time"] if row["time"] else None,
                    pin=row["pin"] if row["pin"] else None
                )
                accounts[acc.account_number] = acc
    except FileNotFoundError:
        pass
    return accounts


def log_transaction(account_number, operation, amount, balance_after):
    # Keep original combined log for backwards-compatibility
    with open(TRANSACTIONS_FILE, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} | {account_number} | {operation} | {amount} | {balance_after}\n")
    # Also write to user-only log
    with open(USER_TRANSACTIONS_FILE, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} | {account_number} | {operation} | {amount} | {balance_after}\n")


def log_admin_action(action_description):
    with open(ADMIN_ACTIONS_FILE, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} | {action_description}\n")


def read_user_transactions():
    try:
        with open(USER_TRANSACTIONS_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def read_admin_actions():
    try:
        with open(ADMIN_ACTIONS_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def export_accounts(accounts, export_path):
    # Use the deep project's CSV schema including time column
    with open(export_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["account_number", "name", "age", "balance", "account_type", "status", "time", "pin"])
        for acc in accounts.values():
            d = acc.to_dict()
            writer.writerow([
                d["account_number"],
                d["name"],
                d["age"],
                d["balance"],
                d["account_type"],
                d["status"],
                d.get("timestamp"),
                d["pin"],
            ])


def import_accounts(import_path):
    accounts = {}
    with open(import_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            acc = Account(
                account_number=row["account_number"],
                name=row["name"],
                age=row["age"],
                account_type=row["account_type"],
                balance=row["balance"],
                status=row.get("status"),
                timestamp=row.get("time") if row.get("time") else None,
                pin=row.get("pin") if row.get("pin") else None,
            )
            accounts[acc.account_number] = acc
    return accounts