
from src.services.banking_service import BankingService,AgeRestrictionError,AccountNotFoundError,InsufficientFundsError,InactiveAccountError
from src.utils.file_manager import (
    read_user_transactions,
    read_admin_actions,
    export_accounts,
    import_accounts,
    log_admin_action,
)

class AdminService:
    def __init__(self, bank: BankingService):
        self.bank = bank
    def get_account(self, account_number):
        return self.bank.get_account(account_number)
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
    def search_by_name(self, name):
        results = []
        for acc in self.bank.accounts.values():
            if acc.name.lower() == name.lower():
                results.append(f"{acc.account_number} | {acc.name} | {acc.account_type} | Balance: {acc.balance} | Status: {acc.status}")
        if not results:
            raise AccountNotFoundError(f"No accounts found for name: {name}")
        return "\n".join(results)   
    def search_by_account_number(self, account_number):
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
    def count_accounts(self):
        return len(self.bank.accounts or {})
        

    @BankingService.autosave
    def force_close_account(self, account_number):
        acc = self.bank.get_account(account_number)
        if not acc:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        acc.status = "Inactive"
        log_admin_action(f"FORCE_CLOSE | {account_number}")
        return f"Account {account_number} has been force-closed by Admin."

    # ---- Additional Admin Features ----
    def list_active_accounts(self):
        active = [acc for acc in self.bank.accounts.values() if acc.status == "Active"]
        if not active:
            return "No active accounts."
        return "\n".join(
            f"{acc.account_number} | {acc.name} | {acc.account_type} | Balance: {acc.balance} | Status: {acc.status}"
            for acc in active
        )

    def list_closed_accounts(self):
        closed = [acc for acc in self.bank.accounts.values() if acc.status != "Active"]
        if not closed:
            return "No closed accounts."
        return "\n".join(
            f"{acc.account_number} | {acc.name} | {acc.account_type} | Balance: {acc.balance} | Status: {acc.status}"
            for acc in closed
        )

    def view_transaction_logs(self):
        user_logs = read_user_transactions()
        admin_logs = read_admin_actions()
        if not user_logs and not admin_logs:
            return "No logs found."
        out = []
        if user_logs:
            out.append("-- User Transactions --\n" + user_logs.strip())
        if admin_logs:
            out.append("-- Admin Actions --\n" + admin_logs.strip())
        return "\n\n".join(out)

    def export_accounts_to_file(self, export_path):
        export_accounts(self.bank.accounts, export_path)
        log_admin_action(f"EXPORT | {export_path}")
        return f"Accounts exported to {export_path}"

    def count_active_accounts(self):
        return sum(1 for acc in self.bank.accounts.values() if acc.status == "Active")

    def delete_all_accounts(self):
        self.bank.accounts.clear()
        self.bank.save_to_disk()   # ✅ call save from BankingService
        log_admin_action("DELETE_ALL_ACCOUNTS")
        return "All accounts deleted."

    def system_exit_with_autosave(self):
        self.bank.save_to_disk()
        log_admin_action("SYSTEM_EXIT_WITH_AUTOSAVE")
        return "Changes saved"

    @BankingService.autosave
    def import_accounts_from_file(self, import_path):
        imported = import_accounts(import_path)
        self.bank.accounts = imported
        if self.bank.accounts:
            self.bank.next_account_number = max(self.bank.accounts.keys()) + 1
        else:
            self.bank.next_account_number = BankingService.START_ACCOUNT_NO
        log_admin_action(f"IMPORT | {import_path}")
        return f"Imported {len(imported)} accounts from {import_path}"


# CLI/runner intentionally kept out of this service module.