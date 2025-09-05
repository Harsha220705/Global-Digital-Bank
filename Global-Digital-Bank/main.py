# Entry point of application so keep it as small as possible
import sys
from src.services.banking_service import BankingService,AgeRestrictionError,AccountNotFoundError,InsufficientFundsError,InactiveAccountError

def main():
    bank=BankingService()
    print("Welcome to Global Digital Bank")

    while True:
        print("\n----Main Menu---\n1. Create Account\n2. Deposit\n3. Withdraw\n4. Balance Enquiry\n5. Close Account\n6. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            try:
                name = input("Enter your name: ")
                age = input("Enter your age: ")
                account_type = input("Enter account type (Savings/Current): ")
                initial_deposit = input("Enter initial deposit amount: ")
                
                acc, msg = bank.create_account(name, age, account_type, initial_deposit)
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
                ok, msg = bank.close_account(acc_no)
                print(msg)
            except AccountNotFoundError as e:
                print(f"Close account failed: Account {e.account_number} not found.")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
        elif choice == '6':
            print("Thank you for banking with us. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
