# Entry point of application so keep it as small as possible
import sys
import time
from src.services.banking_service import BankingService,AgeRestrictionError,AccountNotFoundError,InsufficientFundsError,InactiveAccountError
from src.utils.file_manager import read_user_transactions
def user_menu():
    bank=BankingService()
    print("Welcome to Global Digital Bank")

    while True:
        print("\n---- Main Menu ----")
        print("1. Create Account")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Balance Enquiry")
        print("5. Close Account")
        print("6. Account Rename")
        print("7. Account Type Upgrade")
        print("8. Reopen Closed Account")
        print("9. Minimum Balance Check")
        print("10. Simple Interest Calculator")
        print("11. Daily Transaction Limit")
        print("12. Transfer Funds")
        print("13. Average Balance Calculator")
        print("14. Set PIN / Password")
        print("15. Verify PIN / Password")
        print("16. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            try:
                name = input("Enter your name: ")
                age = input("Enter your age: ")
                account_type = input("Enter account type (Savings/Current): ")
                initial_deposit = input("Enter initial deposit amount: ")
                
                acc, msg = bank.create_account(name, age, account_type, initial_deposit,timestamp=time.strftime("%Y-%m-%d %H:%M:%S"))
                if acc:
                    print(f"Account created successfully! Your account number is {acc.account_number}")
                else:
                    print(f"Failed to create account: {msg}")

            except AgeRestrictionError as e:
                print(f"Failed to create account: {e.message} (Provided age: {e.age})")

            except Exception as e:
                print(f"Error: {str(e)}")
            
        elif choice == '2':
            try:
                acc_no = input("Enter your account number: ")
                amount = float(input("Enter amount to deposit: "))

                ok, msg = bank.deposit(acc_no, amount)
                print(msg)

            except ValueError:
                print("Invalid amount. Please enter a numeric value.")
            except AccountNotFoundError as e:
                print(f"Deposit failed: Account {e.account_number} not found.")
            except InactiveAccountError as e:
                print(str(e))   # message like: "Account 1001 or any other (account number) is not active."
            except InsufficientFundsError as e:   # not really needed for deposit
                print(str(e))
            except Exception as e:
                print(f"Unexpected error: {str(e)}")

        elif choice == '3':
            try:
                acc_no = input("Enter your account number: ")
                amount = float(input("Enter amount to withdraw: "))
                ok, msg = bank.withdraw(acc_no, amount)
                print(msg)
            except ValueError:
                print("Invalid amount. Please enter a numeric value.")
            except AccountNotFoundError as e:
                print(f"Withdrawal failed: Account {e.account_number} not found.")
            except InactiveAccountError as e:
                print(str(e))   # message like: "Account 1001 or any other (account number) is not active."
            except InsufficientFundsError as e:
                print(str(e))
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
        elif choice == '4':
            try:
                acc_no = input("Enter your account number: ")
                acc, msg = bank.balance_inquiry(acc_no)
                if acc:
                    print(msg)
            except AccountNotFoundError as e:
                print(f"Balance enquiry failed: Account {e.account_number} not found.")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
            
            
        elif choice == '5':
            try:
                acc_no = input("Enter your account number: ")
                ok, msg = bank.terminate_account(acc_no)
                print(msg)
            except Exception as e:
                print(f"Error: {str(e)}")
        elif choice == '6':
            try:
                acc_no = input("Enter your account number: ")
                ok, msg = bank.account_rename(acc_no)
            except Exception as e:
                print(f"Error: {str(e)}")
        elif choice == '7':
            acc_no = input("Enter account number: ")
            new_type = input("New type (Savings/Current): ")
            ok, msg = bank.upgrade_account_type(acc_no, new_type)
            print(msg)
        elif choice == '8':
            acc_no = input("Enter account number to reopen: ")
            ok, msg = bank.reopen_account(acc_no)
            print(msg)
        elif choice == '9':
            acc_no = input("Enter account number: ")
            try:
                amount = float(input("Enter hypothetical withdrawal amount: "))
            except ValueError:
                print("Invalid amount.")
                continue
            acc = bank.get_account(acc_no)
            if not acc:
                print("Account not found.")
                continue
            min_req = acc.MIN_BALANCE[acc.account_type]
            projected = round(acc.balance - amount, 2)
            if projected < min_req:
                print(f"Would fail: minimum required balance for {acc.account_type} is {min_req}. Projected: {projected}")
            else:
                print(f"OK: projected balance after withdrawal = {projected}")
        elif choice == '10':
            acc_no = input("Enter account number: ")
            rate = input("Enter annual rate %: ")
            years = input("Enter number of years: ")
            ok, msg = bank.calculate_simple_interest(acc_no, rate, years)
            print(msg)
        elif choice == '11':
            acc_no = input("Enter account number: ")
            try:
                dep_used = bank._get_today_total(int(acc_no), "DEPOSIT")
                wit_used = bank._get_today_total(int(acc_no), "WITHDRAW")
                print(f"Deposit remaining today: {bank.DAILY_DEPOSIT_LIMIT - dep_used}")
                print(f"Withdraw remaining today: {bank.DAILY_WITHDRAW_LIMIT - wit_used}")
            except Exception:
                print("Could not compute daily limits.")
        elif choice == '12':
            from_acc = input("From account: ")
            to_acc = input("To account: ")
            # Show receiver details for verification
            recv = bank.get_account(to_acc)
            if not recv:
                print("Receiver account not found.")
                continue
            print(f"Receiver: {recv.account_number} | {recv.name}")
            confirm = input("Is receiver correct? (Y/N): ").strip().lower()
            if confirm != 'y':
                print("Transfer cancelled.")
                continue
            # Ask for PIN on sender account
            pin = input("Enter your PIN: ")
            try:
                if not bank.verify_pin(from_acc, pin):
                    print("Invalid PIN. Transfer cancelled.")
                    continue
            except AccountNotFoundError as e:
                print(str(e))
                continue
            amount = input("Amount: ")
            ok, msg = bank.transfer_funds(from_acc, to_acc, amount)
            print(msg)
        elif choice == '13':
            print(f"Average balance: {bank.average_balance()}")
        elif choice == '14':
            acc_no = input("Enter account number: ")
            pin = input("Set new PIN: ")
            ok, msg = bank.set_pin(acc_no, pin)
            print(msg)
        elif choice == '15':
            acc_no = input("Enter account number: ")
            pin = input("Enter PIN: ")
            try:
                is_ok = bank.verify_pin(acc_no, pin)
                print("PIN correct" if is_ok else "Invalid PIN")
            except AccountNotFoundError as e:
                print(str(e))
        elif choice == '16':
            print("Thank you for banking with us. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    user_menu()
