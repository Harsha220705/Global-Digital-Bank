# Entry point of application so keep it as small as possible
import sys
import time
from src.services.banking_service import BankingService,AgeRestrictionError,AccountNotFoundError,InsufficientFundsError,InactiveAccountError
from src.utils.file_manager import read_user_transactions
from src.services.loan_services import LoanService
def user_menu(account_number=None):
    bank=BankingService()
    loan_service = LoanService()
    print("Welcome to Global Digital Bank")
    
    # If no account number provided, ask for it (for backward compatibility)
    if not account_number:
        account_number = input("Enter your account number: ")

    while True:
        print("\n====== Main Menu =======")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Balance Enquiry")
        print("4. Close Account")
        print("5. Account Rename")
        print("6. Account Type Upgrade")
        print("7. Reopen Closed Account")
        print("8. Minimum Balance Check")
        print("9. Simple Interest Calculator (Savings : 7.5% , Current : 9.5%)")
        print("10. Daily Transaction Limit")
        print("11. Transfer Funds")
        print("12. Average Balance Calculator")
        print("13. Take Loan")
        print("14. Loan Details")
        print("15. Exit")
        choice = input("Enter your choice: ")
          
        if choice == '1':
            try:
                pin = input("Enter your PIN: ")
                
                # Verify PIN before deposit
                if not bank.verify_pin(account_number, pin):
                    print("Invalid PIN. Deposit cancelled.")
                    continue
                
                amount = float(input("Enter amount to deposit: "))
                mode = input("Is this deposit for Loan Repayment? (Y/N): ").strip().lower()
                if mode == 'y':
                    ok_r, msg_r, applied = loan_service.repay(int(account_number), amount)
                    print(msg_r)
                    remainder = round(amount - applied, 2)
                    if remainder > 0:
                        ok, msg = bank.deposit(account_number, remainder)
                        print(msg)
                else:
                    ok, msg = bank.deposit(account_number, amount)
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
            print("Loading...")
            time.sleep(3)

        elif choice == '2':
            try:
                pin = input("Enter your PIN: ")
                
                # Verify PIN before withdrawal
                if not bank.verify_pin(account_number, pin):
                    print("Invalid PIN. Withdrawal cancelled.")
                    continue
                
                amount = float(input("Enter amount to withdraw: "))
                ok, msg = bank.withdraw(account_number, amount)
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
            print("Loading...")
            time.sleep(3)
        elif choice == '3':
            try:
                acc, msg = bank.balance_inquiry(account_number)
                if acc:
                    print(msg)
            except AccountNotFoundError as e:
                print(f"Balance enquiry failed: Account {e.account_number} not found.")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
            print("Loading...")
            time.sleep(3)
            
            
        elif choice == '4':
            try:
                ok, msg = bank.terminate_account(account_number)
                print(msg)
            except Exception as e:
                print(f"Error: {str(e)}")
            print("Loading...")
            time.sleep(3)
        elif choice == '5':
            try:
                ok, msg = bank.account_rename(account_number)
            except Exception as e:
                print(f"Error: {str(e)}")
            print("Loading...")
            time.sleep(3)
        elif choice == '6':
            new_type = input("New type (Savings/Current): ")
            ok, msg = bank.upgrade_account_type(account_number, new_type)
            print(msg)
            print("Loading...")
            time.sleep(3)
        elif choice == '7':
            ok, msg = bank.reopen_account(account_number)
            print(msg)
            print("Loading...")
            time.sleep(3)
        elif choice == '8':
            try:
                amount = float(input("Enter hypothetical withdrawal amount: "))
            except ValueError:
                print("Invalid amount.")
                continue
            acc = bank.get_account(account_number)
            if not acc:
                print("Account not found.")
                continue
            min_req = acc.MIN_BALANCE[acc.account_type]
            projected = round(acc.balance - amount, 2)
            if projected < min_req:
                print(f"Would fail: minimum required balance for {acc.account_type} is {min_req}. Projected: {projected}")
            else:
                print(f"OK: projected balance after withdrawal = {projected}")
            print("Loading...")
            time.sleep(3)
        elif choice == '9':
            years = input("Enter number of years: ")
            # Get account to determine rate
            acc = bank.get_account(account_number)
            if not acc:
                print("Account not found.")
                continue
            # Fixed rates based on account type
            if acc.account_type == "Savings":
                rate = "7.5"
            elif acc.account_type == "Current":
                rate = "9.5"
            else:
                rate = "7.5"  # default
            print(f"Interest rate for {acc.account_type} account: {rate}% per annum")
            ok, msg = bank.calculate_simple_interest(account_number, rate, years)
            print(msg)
            print("Loading...")
            time.sleep(3)
        elif choice == '10':
            try:
                dep_used = bank._get_today_total(int(account_number), "DEPOSIT")
                wit_used = bank._get_today_total(int(account_number), "WITHDRAW")
                print(f"Deposit remaining today: {bank.DAILY_DEPOSIT_LIMIT - dep_used}")
                print(f"Withdraw remaining today: {bank.DAILY_WITHDRAW_LIMIT - wit_used}")
            except Exception:
                print("Could not compute daily limits.")
            print("Loading...")
            time.sleep(3)
        elif choice == '11':
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
                if not bank.verify_pin(account_number, pin):
                    print("Invalid PIN. Transfer cancelled.")
                    continue
            except AccountNotFoundError as e:
                print(str(e))
                continue
            amount = input("Amount: ")
            ok, msg = bank.transfer_funds(account_number, to_acc, amount)
            print(msg)
            print("Loading...")
            time.sleep(3)
        elif choice == '12':
            print(f"Average balance: {bank.average_balance()}")
            print("Loading...")
            time.sleep(3)
        elif choice == '13':
            # Take Loan
            acc = bank.get_account(account_number)
            if not acc:
                print("Account not found.")
                continue
            print(f"Eligible limit for {acc.account_type}: ₹{LoanService.get_max_limit_for_account_type(acc.account_type):,.0f}")
            amount = input("Enter loan amount: ")
            years = input("Choose tenure (3 or 4 years): ")
            try:
                ok, msg, record = loan_service.take_loan(acc, float(amount), int(years))
                print(msg)
                if ok and record:
                    # Credit principal to user's balance bypassing daily limit
                    okd, msgd = bank.credit_loan_disbursal(account_number, record["principal"])
                    print(f"Loan amount credited to your account. {msgd}")
            except Exception as e:
                print(f"Error: {str(e)}")
            print("Loading...")
            time.sleep(3)
        elif choice == '14':
            # Loan Details
            try:
                print(loan_service.details(int(account_number)))
            except Exception as e:
                print(f"Error: {str(e)}")
            print("Loading...")
            time.sleep(3)
        elif choice == '15':
            print("Thank you for banking with us. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    user_menu()
