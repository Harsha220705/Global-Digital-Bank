# This is the "service layer"
# It acts as the middle layer between  the Account model (business rules)
# and file_manager utilities (storage and logging).
from src.models.account import Account
from  src.utils.file_manager import load_accounts, save_accounts, log_transaction
class BankingService:
    START_ACCOUNT_NO = 1001
    def __init__(self):
        # load accounts from file on starup
        self.accounts = load_accounts()
        if self.accounts:
            # if account exist, continue from the max account number
            self.next_account_number = max(self.accounts.keys()) + 1 # 1001, 1002, 1003 , 1004
        else :
            # otherwise,start fresh from 1001
            self.next_account_number = BankingService.START_ACCOUNT_NO
 
   
    def save_to_disk(self):
        #save all accounts to persistent storage(CSV files)
        save_accounts(self.accounts)
 
 
    def create_account(self, name,age, account_type, intial_deposit=0):
        # ---- Basic Validation Checks ----
        if not name.strip():
            return None, "Name cannot be empty"

        if int(age) < 18:
            return None, "Age must be 18 or above"
            

        # Normalize account type (capitalize first letter)
        account_type = account_type.title()
        if account_type not in Account.MIN_BALANCE:
            # check if account type is valid
            return None , f"Invalid Account type. Choose from {list(Account.MIN_BALANCE.keys())}"
        min_req = Account.MIN_BALANCE[account_type]
        if float(intial_deposit) < min_req:
            return None, f"Intial deposit must be at least {min_req}"
       
        acc_no = self.next_account_number
        acc = Account(acc_no, name,age, account_type, balance=float(intial_deposit))
        self.accounts[acc_no] = acc
        # 1001, 10002, 1003
        self.next_account_number += 1


        log_transaction(acc_no, "CREATE", intial_deposit, acc.balance)
        self.save_to_disk()
        return acc, "Account created succesfully"
   
 
    def get_account(self, account_number):
        return self.accounts.get(int(account_number))
   
 
    def deposit(self,account_number, amount):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.status != "Active":
            return False , "Account is not Active"
       
        ok, msg = acc.deposit(amount)
        if ok:
            log_transaction(acc.account_number, "DEPOSIT", amount, acc.balance)
            self.save_to_disk()
        return ok, msg
   
    def withdraw(self, account_number, amount):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.staus != "Active":
            return False , "Account is not Active"
       
        ok, msg = acc.withdraw(amount)
        if ok:
            log_transaction(acc.account_number, "WITHDRAW", amount, acc.balance)
            self.save_to_disk()
        return ok, msg
   
    def balance_inquiry(self, account_number):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        return acc, f"Balance: {acc.balance}"
   
    def close_account(self, account_number):
         acc = self.get_account(account_number)
         if not acc:
            return False, "Account not Found"
         
         acc.status = "Inactive"
         log_transaction(acc.account_number, "CLOSE" , None, acc.balance)
         self.save_to_disk()
         return True , "Account closed succesfully"