import random
import time

class Account:
    def __init__(self, account_number, name, age, balance, account_type, pin=None):
        self.account_number = account_number
        self.name = name
        self.age = age
        self.balance = balance
        self.account_type = account_type
        self.pin = pin
        self.status = "Active"

    def generate_acc_num(self):
        return [random.randint(0,9) for _ in range(12) ]

    def create_account(self,name,age,initial_deposit,account_type,pin,time_generated):
        account_number = self.generate_acc_num()
        self.time_generated = time_generated
        if self.initial_deposit < self.get_minimum_balance():
            print(f"Initial deposit must be at least {self.get_minimum_balance()} for {account_type} account.")
            return None
        new_account = Account(account_number, name, age, initial_deposit, account_type, pin)
        return new_account
        

    def deposit(self, amount):
        pass

    def withdraw(self, amount):
        pass

    def check_balance(self):
        pass

    def close_account(self):
        pass

    def account_close(self):
        pass

    def list_active_accounts(self):
        pass

    def transfer_funds(self, target_account, amount):
        pass
    def transaction_history(self):
        pass




    def get_minimum_balance(self):
        if self.account_type == "Savings":
            return 500
        elif self.account_type == "Current":
            return 1000
        return 0.0

    def is_active(self):
        return self.status == "Active"
    
    def __str__(self):
        return f"Account Holder Name: {self.name}, Account Number: {self.account_number}, Balance: {self.balance}, Status: {self.status}"
    
