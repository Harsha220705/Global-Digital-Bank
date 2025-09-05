
from src.services.banking_service import BankingService,AgeRestrictionError,AccountNotFoundError,InsufficientFundsError,InactiveAccountError

class AdminService:
    def __init__(self, bank: BankingService):
        self.bank = bank
    def get_account(self, account_number):
        return self.bank.accounts.get(int(account_number))
    def view_all_accounts(self):
        if not self.bank.accounts:
            raise AccountNotFoundError(f"Account {self.bank.accounts} not found.")
        accounts_list = []
        for acc in self.bank.accounts.values():
            accounts_list.append(
                f"{acc.account_number} | {acc.name} | {acc.account_type} | Balance: {acc.balance} | Status: {acc.status}"
            )
        return "\n".join(accounts_list)

    def search_account(self, account_number):
        acc = self.bank.get_account(account_number)
        if acc:
            return f"{acc.account_number} | {acc.name} | {acc.account_type} | Balance: {acc.balance} | Status: {acc.status}"
        else:
            raise AccountNotFoundError(f"Account {account_number} not found.")
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