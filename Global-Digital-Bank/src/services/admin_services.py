
from src.services.banking_service import BankingService,AgeRestrictionError,AccountNotFoundError,InsufficientFundsError,InactiveAccountError

class AdminService:
    def __init__(self, bank: BankingService):
        self.bank = bank
    def get_account(self, ccount_number):
        return self.bank.accounts.get(ccount_number)
    def view_all_accounts(self):
        if not self.bank.accounts:
            raise AccountNotFoundError(f"Account {self.bank.accounts} not found.")
        accounts_list = []
        for acc in self.bank.accounts.values():
            accounts_list.append(
                f"{acc.account_number} | {acc.name} | {acc.account_type} | Balance: {acc.balance} | Status: {acc.status}"
            )
        return "\n".join(accounts_list)

    def search_name(self, name):
        for acc in self.bank.accounts.values():
            if acc.name.lower() == name.lower():   # exact name match
                return f"{acc.name} | {acc.account_number} | {acc.account_type} | Balance: {acc.balance} | Status: {acc.status}"
            raise AccountNotFoundError(f"Account with name '{name}' not found.")

    @BankingService.autosave
    def reactivate_account(self, account_number):
        acc = self.bank.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        if acc.status == "Active":
            return f"Account {account_number} is already active."
        acc.status = "Active"
        return f"Account {account_number} has been reactivated."

    @BankingService.autosave
    def force_close_account(self, account_number):
        acc = self.bank.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        acc.status = "Inactive"
        return f"Account {account_number} has been force-closed by Admin."
    

    def search_by_name(self, name):
        matches = [
        acc for acc in self.bank.accounts.values()
        if name.lower() in acc.name.lower()
        ]
        if not matches:
            raise AccountNotFoundError(f"No accounts found for name '{name}'")
        return "\n".join(f"{acc.account_number} | {acc.name} | {acc.account_type} | Balance: {acc.balance} | Status: {acc.status}"
        for acc in matches
    )
    

    def search_by_account_number(self, account_number):
        try:
            acc = self.bank.get_account(account_number)   # this expects an int or str of digits
        except ValueError:
            raise AccountNotFoundError(f"Invalid account number '{account_number}'")

        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")

        return f"{acc.account_number} | {acc.name} | {acc.account_type} | Balance: {acc.balance} | Status: {acc.status}"
