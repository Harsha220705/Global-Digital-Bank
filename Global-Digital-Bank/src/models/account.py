class Account:
    MIN_BALANCE = {"Savings": 500, "Current": 1000}
    MAX_SINGLE_DEPOSIT = 100000.0

    def __init__(self, 
                 account_number, 
                 name, 
                 age, 
                 account_type,
                 balance = 0.0,
                 status = "Active",
                 timestamp=None,pin=None):
        
        self.account_number = int(account_number)
        self.name = name.strip()
        self.age = int(age)
        self.account_type = account_type.title()
        if self.account_type not in Account.MIN_BALANCE:
            raise ValueError(f"Invalid account type: {self.account_type}")
        self.balance = float(balance)
        self.status = status
        self.timestamp = timestamp if timestamp else None
         # account creation time
         # can be used for interest calculation later
            # or account age verification
        self.pin = pin

    def deposit(self, amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False, "Invalid Amount"
        
        if self.status != "Active":
            return False, "Account is inactive"

        if amount <= 0:
            return False, "Deposit must be positive"
        if amount >  Account.MAX_SINGLE_DEPOSIT:
            return False, f"Deposit exceeds single-deposit limit {Account.MAX_SINGLE_DEPOSIT}"
        
        self.balance += amount

        return True, f"Deposit Successful. New Balance: {self.balance:.2f}"
    

    def withdraw(self, amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False, "Invalid Amount"
        
        if self.status != "Active":
            return False, "Account is inactive"
        if amount <= 0:
            return False, "Withdrawal must be positive"
        

        min_required = Account.MIN_BALANCE[self.account_type]
        if round(self.balance - amount, 2) < min_required:
            return False, f"Insufficient funds. Minimum required balance for {self.account_type}: {min_required}"

        self.balance -= amount
        return True, f"Withdrawal successful.\nNew Balance: {self.balance}"
    

    def to_dict(self):
        return {
            "account_number": self.account_number,
            "name": self.name,
            "age": self.age,
            "balance": self.balance,
            "account_type": self.account_type,
            "status": self.status,
            "timestamp": self.timestamp if self.timestamp else "",
            "pin": self.pin if self.pin else "", 
        }
    
    def __str__(self):
        return f"[{self.account_number}] {self.name} ({self.account_type}) - Balance: {self.balance} - {self.status}"