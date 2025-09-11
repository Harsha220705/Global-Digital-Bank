import main as user_main
from src.services.admin_services import AdminService
from src.services.banking_service import BankingService, AccountNotFoundError
from src.utils.file_manager import read_user_transactions, read_admin_actions
from src.services.loan_services import LoanService


def user_login():
    """Handle user login with account number and PIN verification"""
    bank = BankingService()
    
    print("\n---- User Login ----")
    print("1. Login")
    print("2. Create New Account")
    choice = input("Enter your choice: ")
    if choice == '1':
        account_number = input("Enter your account number: ")
    elif choice == '2':
        import new_account
        new_account.user_menu()
        return
    else:
        print("Invalid choice. Try again.")
        return
    
    # Check if account exists
    account = bank.get_account(account_number)
    if not account:
        print(f"Account {account_number} not found.")
        print("Redirecting to new account creation...")
        import new_account
        new_account.user_menu()
        return
    
    # Account exists, verify PIN
    pin = input("Enter your PIN: ")
    try:
        if bank.verify_pin(account_number, pin):
            print("Login successful! Welcome to Global Digital Bank.")
            user_main.user_menu(account_number)
        else:
            print("Invalid PIN. Access denied.")
    except AccountNotFoundError as e:
        print(str(e))


def start():
    print("---- Welcome to Global Digital Bank ----")
    print("\nLogin as:")
    print("1. User")
    print("2. Admin")
    try:
        choice = int(input("Enter your choice: "))
    except ValueError:
        print("Invalid choice. Try again.")
        return

    if choice == 1:
        user_login()
    elif choice == 2:
        key = input("Enter security key: ")
        if key != "admin123":
            print("Access denied. Wrong key.")
            return
        bank = BankingService()
        admin = AdminService(bank)
        loan_service = LoanService()
        while True:
            print("\n---- Admin Features ----")
            print("1. List All Active Accounts")
            print("2. List All Closed Accounts")
            print("3. Transaction Log File")
            print("4. Search by Account Number")
            print("5. Transaction History Viewer")
            print("6. Youngest Account Holder")
            print("7. Oldest Account Holder")
            print("8. Top N Accounts by Balance")
            print("9. Average Balance Calculator")
            print("10. Count Active Accounts")
            print("11. Delete All Accounts")
            print("12. System Exit with Autosave")
            print("13. Exit")
            print("14. List Active Loans (Acc No | Name)")
            admin_choice = input("Enter your choice: ")

            if admin_choice == '1':
                print(admin.list_active_accounts())
            elif admin_choice == '2':
                print(admin.list_closed_accounts())
            elif admin_choice == '3':
                logs = read_user_transactions()
                actions = read_admin_actions()
                out = []
                if logs:
                    out.append("-- User Transactions --\n" + logs.strip())
                if actions:
                    out.append("-- Admin Actions --\n" + actions.strip())
                print("\n\n".join(out) if out else "No logs found.")
            elif admin_choice == '4':
                acc_no = input("Enter account number: ")
                try:
                    print(admin.search_by_account_number(acc_no))
                except AccountNotFoundError as e:
                    print(str(e))
            elif admin_choice == '5':
                acc_no = input("Enter account number: ")
                print(bank.transaction_history(acc_no))
            elif admin_choice == '6':
                acc = bank.youngest_account_holder()
                print(f"Youngest: {acc.account_number} | {acc.name} | Age: {acc.age}" if acc else "No accounts.")
            elif admin_choice == '7':
                acc = bank.oldest_account_holder()
                print(f"Oldest: {acc.account_number} | {acc.name} | Age: {acc.age}" if acc else "No accounts.")
            elif admin_choice == '8':
                n = input("Enter N: ")
                top = bank.top_n_accounts_by_balance(n)
                if not top:
                    print("No accounts or invalid N.")
                else:
                    for a in top:
                        print(f"{a.account_number} | {a.name} | Balance: {a.balance}")
            # elif admin_choice == '9':
            #     path = input("Enter export file path: ")
            #     print(admin.export_accounts_to_file(path))
            elif admin_choice == '9':
                print(f"Average balance: {bank.average_balance()}")
            elif admin_choice == '10':
                print(f"Active accounts: {admin.count_active_accounts()}")
            elif admin_choice == '11':
                confirm = input("Are you sure you want to delete ALL accounts? (Y/N): ").strip().lower()
                if confirm == 'y':
                    print(admin.delete_all_accounts())
                else:
                    print("Cancelled.")
            elif admin_choice == '12':
                print(admin.system_exit_with_autosave())
            # elif admin_choice == '14':
            #     path = input("Enter import file path: ")
            #     print(admin.import_accounts_from_file(path))
            elif admin_choice == '13':
                break
            elif admin_choice == '14':
                active = loan_service.get_active_loans_list()
                if not active:
                    print("No active loans.")
                else:
                    for acc_no, name in active:
                        print(f"{acc_no} | {name}")
            else:
                print("Invalid choice.")
    else:
        print("Invalid choice. Try again.")


if __name__ == "__main__":
    start()

