from src.models.accounts import Account
import datetime
def main():
    while True:
        print("--- Welcome to Global Digital Bank ---")
        print("\n1) Create Account \n2) Deposit \n3) Withdraw \n4) Check Balance \n5) Close Account \n6) List All Active Accounts \n7) Transfer Funds \n8) Transaction History \n9) Exit")
        try:
            choice = int(input("Enter your choice: "))
            choice = int(choice)
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 9.")
            continue
        except KeyboardInterrupt:
            print("\nExiting the application.")
            break
        if choice == 1:
            print("Creating a new account...")
            name = input("Enter your Account Holder Name: ")
            age = int(input("Enter your Age: "))
            initial_deposit = float(input("Enter initial deposit amount: "))
            account_type = input("Enter account type (Savings/Current): ")
            pin = input("Set a 4-digit PIN for your account: ")
            time_generated  = datetime.datetime.now()
            
            Account.create_account(name,age,initial_deposit,account_type,pin,time_generated)
        elif choice == 2:
            Account.deposit()
        elif choice == 3:
            Account.withdraw()
        elif choice == 4:
            Account.check_balance()
        elif choice == 5:
            Account.close_account()
        elif choice == 6:
            Account.list_active_accounts()
        elif choice == 7:
            Account.transfer_funds()
        elif choice == 8:
            Account.transaction_history()
        elif choice == 9:
            print("Thank you for using Global Digital Bank. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")



if __name__ == "__main__":
    main()