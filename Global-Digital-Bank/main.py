# Entry point of application so keep it as small as possible

from src.services.banking_service import BankingService

def main():
    bank=BankingService()
    print("Welcome to Global Digital Bank")

    while True:
        print("\n----Main Menu---\n1. Create Account\n2. Deposit\n3. Withdraw\n4. Balance Enquiry\n5. Close Account\n6. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            name = input("Enter your name: ")
            age = input("Enter your age: ")
            account_type = input("Enter account type (Savings/Current): ")
            initial_deposit = input("Enter initial deposit amount: ")
            acc, msg = bank.create_account(name, age, account_type, initial_deposit)
            if acc:
                print(f"Account created successfully! Your account number is {acc.account_number}")
            else:
                print(f"Failed to create account: {msg}")
        elif choice == '2':
            acc_no = input("Enter your account number: ")
            amount = float(input("Enter amount to deposit: "))
            ok, msg = bank.deposit(acc_no, amount)
            print(msg)
        elif choice == '3':
            acc_no = input("Enter your account number: ")
            amount = float(input("Enter amount to withdraw: "))
            ok, msg = bank.withdraw(acc_no, amount)
            print(msg)
        elif choice == '4':
            acc_no = input("Enter your account number: ")
            acc, msg = bank.balance_inquiry(acc_no)
            if acc:
                print(msg)
            else:
                print(f"Error: {msg}")
        elif choice == '5':
            acc_no = input("Enter your account number: ")
            ok, msg = bank.close_account(acc_no)
            print(msg)
        elif choice == '6':
            print("Thank you for banking with us. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
