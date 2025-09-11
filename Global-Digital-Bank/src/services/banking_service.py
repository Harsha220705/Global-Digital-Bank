# This is the "service layer"
# It acts as the middle layer between  the Account model (business rules)
# and file_manager utilities (storage and logging).
from src.models.account import Account
import time,datetime
from  src.utils.file_manager import load_accounts, save_accounts, log_transaction
from  src.utils.file_manager import USER_TRANSACTIONS_FILE
class BankingService:
    START_ACCOUNT_NO = 1001
    DAILY_DEPOSIT_LIMIT = 200000.0
    DAILY_WITHDRAW_LIMIT = 200000.0
    def __init__(self):
        # load accounts from file on starup
        self.accounts = load_accounts()
        if self.accounts:
            # if account exist, continue from the max account number
            self.next_account_number = max(self.accounts.keys()) + 1 # 1001, 1002, 1003 , 1004
        else :
            # otherwise,start fresh from 1001
            self.next_account_number = BankingService.START_ACCOUNT_NO
    # Decorater to AutoSave after any opertaion modifies the data
    def autosave(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)   # run the actual method
            self.save_to_disk()                    # always save after success
            return result
        return wrapper
    
    def save_to_disk(self):
        #save all accounts to persistent storage(CSV files)
        save_accounts(self.accounts)
    
    @autosave
    def create_account(self, name,age, account_type, intial_deposit=0,timestamp=None):
        # ---- Basic Validation Checks ----
        if not name.strip():
            return None, "Name cannot be empty"

        if int(age) < 18:
            raise AgeRestrictionError(age)
            

        account_type = account_type.title()
        if account_type not in Account.MIN_BALANCE:
            # check if account type is valid
            return None , f"Invalid Account type. Choose from {list(Account.MIN_BALANCE.keys())}"
        min_req = Account.MIN_BALANCE[account_type]
        if float(intial_deposit) < min_req:
            return None, f"Intial deposit must be at least {min_req}"
       
        acc_no = self.next_account_number
        acc = Account(acc_no, name,age, account_type, balance=float(intial_deposit),timestamp=timestamp)
        self.accounts[acc_no] = acc
        
        self.next_account_number += 1


        log_transaction(acc_no, "CREATE", intial_deposit, acc.balance)
        
        return acc, "Account created succesfully"
   

    def get_account(self, account_number):
        return self.accounts.get(int(account_number))
   
    @autosave
    def deposit(self, account_number, amount):
        acc = self.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        if acc.status != "Active":
            raise InactiveAccountError(f"Account {account_number} is not active.")
        # Daily limit check for deposits
        today_total = self._get_today_total(acc.account_number, "DEPOSIT")
        try:
            amt_f = float(amount)
        except (TypeError, ValueError):
            amt_f = 0.0
        if today_total + amt_f > BankingService.DAILY_DEPOSIT_LIMIT:
            return False, f"Daily deposit limit exceeded. Limit: {BankingService.DAILY_DEPOSIT_LIMIT}"
        ok, msg = acc.deposit(amount)
        if ok:
            log_transaction(acc.account_number, "DEPOSIT", amount, acc.balance)
            self.save_to_disk()
    
        return ok, msg

    @autosave
    def credit_loan_disbursal(self, account_number, amount):
        """Credit loan amount to balance bypassing daily deposit limit.

        Logs as LOAN_CREDIT.
        """
        acc = self.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        if acc.status != "Active":
            raise InactiveAccountError(f"Account {account_number} is not active.")
        try:
            amt_f = float(amount)
        except (TypeError, ValueError):
            amt_f = 0.0
        if amt_f <= 0:
            return False, "Invalid amount."
        acc.balance += amt_f
        log_transaction(acc.account_number, "LOAN_CREDIT", amt_f, acc.balance)
        self.save_to_disk()
        return True, f"Loan amount credited. New Balance: {acc.balance:.2f}"
    @autosave
    def withdraw(self, account_number, amount):
        acc = self.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        if acc.status != "Active":
            raise InactiveAccountError(f"Account {account_number} is not active.")
        # Daily limit check for withdrawals
        today_total = self._get_today_total(acc.account_number, "WITHDRAW")
        try:
            amt_f = float(amount)
        except (TypeError, ValueError):
            amt_f = 0.0
        if today_total + amt_f > BankingService.DAILY_WITHDRAW_LIMIT:
            return False, f"Daily withdrawal limit exceeded. Limit: {BankingService.DAILY_WITHDRAW_LIMIT}"
       
        ok, msg = acc.withdraw(amount)
        if ok:
            log_transaction(acc.account_number, "WITHDRAW", amount, acc.balance)
            self.save_to_disk()
        return ok, msg
    @autosave
    def terminate_account(self, account_number):
        acc = self.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        if acc.status != "Active":
            raise InactiveAccountError(account_number)

        # Force withdraw everything without min balance check so no need to have min balance check
        if acc.balance > 0:
            withdrawn_amount = acc.balance
            acc.balance = 0
            log_transaction(acc.account_number, "WITHDRAW_FULL", None, withdrawn_amount)

        # close account
        acc.status = "Inactive"
        log_transaction(acc.account_number, "CLOSE", None, 0)
        self.save_to_disk()
        return True, "Account closed successfully"

        
    
   
    def balance_inquiry(self, account_number):
        acc = self.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        return acc, f"Balance: {acc.balance}"
    
    @autosave
    def close_account(self, account_number):
         acc = self.get_account(account_number)
         if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
         
         acc.status = "Inactive"
         log_transaction(acc.account_number, "CLOSE" , None, acc.balance)
         self.save_to_disk()
         return True , "Account closed succesfully"

    # ----- Additional Features -----
    def upgrade_account_type(self, account_number, new_account_type):
        acc = self.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        new_type = new_account_type.title()
        if new_type not in Account.MIN_BALANCE:
            return False, f"Invalid Account type. Choose from {list(Account.MIN_BALANCE.keys())}"
        acc.account_type = new_type
        self.save_to_disk()
        return True, f"Account {account_number} upgraded to {new_type}"

    @autosave
    def reopen_account(self, account_number):
        acc = self.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        if acc.status == "Active":
            return False, f"Account {account_number} is already active."
        acc.status = "Active"
        return True, f"Account {account_number} reopened."

    def calculate_simple_interest(self, account_number, rate_percent, years):
        acc = self.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        try:
            r = float(rate_percent) / 100.0
            t = float(years)
        except (TypeError, ValueError):
            return False, "Invalid rate or years"
        interest = round(acc.balance * r * t, 2)
        return True, f"Simple interest: {interest} on balance {acc.balance} at {rate_percent}% for {years} years"

    @autosave
    def transfer_funds(self, from_account, to_account, amount):
        from_acc = self.get_account(from_account)
        to_acc = self.get_account(to_account)
        if not from_acc:
            raise AccountNotFoundError(f"Account {from_account} not found.")
        if not to_acc:
            raise AccountNotFoundError(f"Account {to_account} not found.")
        if from_acc.status != "Active" or to_acc.status != "Active":
            return False, "Both accounts must be active"
        # Enforce daily limit on withdrawals from source
        today_total = self._get_today_total(from_acc.account_number, "WITHDRAW")
        try:
            amt_f = float(amount)
        except (TypeError, ValueError):
            amt_f = 0.0
        if today_total + amt_f > BankingService.DAILY_WITHDRAW_LIMIT:
            return False, f"Daily withdrawal limit exceeded. Limit: {BankingService.DAILY_WITHDRAW_LIMIT}"
        # Perform withdrawal from source
        ok, msg = from_acc.withdraw(amount)
        if not ok:
            return False, msg
        # Deposit to destination
        ok, msg = to_acc.deposit(amount)
        if not ok:
            # rollback source if destination deposit fails
            from_acc.balance += amt_f
            return False, msg
        # Log both legs
        log_transaction(from_acc.account_number, "TRANSFER_OUT", amount, from_acc.balance)
        log_transaction(to_acc.account_number, "TRANSFER_IN", amount, to_acc.balance)
        self.save_to_disk()
        return True, f"Transferred {amount} from {from_acc.account_number} to {to_acc.account_number}"

    def transaction_history(self, account_number):
        try:
            acc_no_int = int(account_number)
        except ValueError:
            raise AccountNotFoundError(account_number)
        try:
            with open(USER_TRANSACTIONS_FILE, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            return "No transactions found."
        history = [line.strip() for line in lines if f"| {acc_no_int} |" in line]
        if not history:
            return "No transactions found."
        return "\n".join(history)

    def average_balance(self):
        if not self.accounts:
            return 0.0
        total = sum(acc.balance for acc in self.accounts.values())
        return round(total / len(self.accounts), 2)

    def youngest_account_holder(self):
        if not self.accounts:
            return None
        return min(self.accounts.values(), key=lambda a: a.age)

    def oldest_account_holder(self):
        if not self.accounts:
            return None
        return max(self.accounts.values(), key=lambda a: a.age)

    def top_n_accounts_by_balance(self, n):
        try:
            n_int = int(n)
        except (TypeError, ValueError):
            return []
        return sorted(self.accounts.values(), key=lambda a: a.balance, reverse=True)[:n_int]

    def set_pin(self, account_number, pin):
        acc = self.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        acc.pin = str(pin)
        self.save_to_disk()
        return True, "PIN set successfully"

    def verify_pin(self, account_number, pin):
        acc = self.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        return str(acc.pin) == str(pin)

    # ----- Helpers -----
    def _get_today_total(self, account_number, operation):
        from datetime import datetime as dt
        today_prefix = dt.now().strftime("%Y-%m-%d")
        try:
            with open(USER_TRANSACTIONS_FILE, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            return 0.0
        total = 0.0
        for line in lines:
            if not line.startswith(today_prefix):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 5:
                continue
            try:
                acc_no = int(parts[1])
            except ValueError:
                continue
            op = parts[2]
            amt_str = parts[3]
            if acc_no == int(account_number) and op == operation:
                try:
                    amt = float(amt_str) if amt_str != "None" else 0.0
                except ValueError:
                    amt = 0.0
                total += amt
        return total
    @autosave
    def account_rename(self, account_number):
         acc = self.get_account(account_number)
         if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
         new_name = input("Enter new name: ").strip()
         if not new_name:
            return False, "Name cannot be empty"
         acc.name = new_name
         self.save_to_disk()
         return True , f"Account renamed successfully to {new_name}"
class AgeRestrictionError(Exception):
    def __init__(self, age, message="Age must be 18 or above to create an account"):
        self.age = age
        self.message = message
        super().__init__(self.message)
class AccountNotFoundError(Exception):
    def __init__(self, account_number, message="Account not found"):
        self.account_number = account_number
        self.message = message
        super().__init__(self.message)
class InsufficientFundsError(Exception):
    def __init__(self, balance, amount, message="Insufficient funds for withdrawal"):
        self.balance = balance
        self.amount = amount
        self.message = message
        super().__init__(self.message)
class InactiveAccountError(Exception):
    def __init__(self, account_number, message=None):
        self.account_number = account_number
        self.message = message or f"Account {account_number} is not active."
        super().__init__(self.message)