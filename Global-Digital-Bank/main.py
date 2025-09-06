# Entry point of application so keep it as small as possible
import sys
import time
from src.services.banking_service import BankingService,AgeRestrictionError,AccountNotFoundError,InsufficientFundsError,InactiveAccountError
from src.services.admin_services import AdminService
def main():
    bank=BankingService()
    print("Welcome to Global Digital Bank")

    while True:
        print("\n----Main Menu---\n1. Create Account\n2. Deposit\n3. Withdraw\n4. Balance Enquiry\n5. Close Account\n6. Account Rename \n7. Exit \n8. Admin Login")
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
            print("Thank you for banking with us. Goodbye!")
            break
        elif choice == '8':   # Admin section
            password = input("Enter admin password: ")
            if password == "admin123": 
                admin = AdminService(bank)
                while True:
                    print("\n----Admin Menu---\n1. View all accounts\n2. Search account by name   \n 3.Search by Account number \n4. Reactivate account\n5. Force close account\n6. Back to Main Menu")
                    admin_choice = input("Enter your choice: ")

                    if admin_choice == '1':
                        print(admin.view_all_accounts())
                    elif admin_choice == '2':
                        name = input("Enter account holder name: ")
                        try:
                            print(admin.search_by_name(name))   # ✅ now using search_by_name
                        except AccountNotFoundError as e:
                            print(str(e))
                    elif admin_choice =='3':
                        acc_no =input("enter the accout number")
                        try:
                            print(admin.search_by_account_number(acc_no))
                        except AccountNotFoundError as e:
                            print(str(e))
                    elif admin_choice == '4':
                        acc_no = input("Enter account number to reactivate: ")
                        print(admin.reactivate_account(acc_no))
                    elif admin_choice == '5':
                        acc_no = input("Enter account number to close: ")
                        print(admin.force_close_account(acc_no))
                    elif admin_choice == '6':
                        break
                    else:
                        print("Invalid choice.")
            else:
                print("Access denied. Wrong password.")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
