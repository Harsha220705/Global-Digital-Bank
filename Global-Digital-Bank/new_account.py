import sys
import time
from src.services.banking_service import BankingService,AgeRestrictionError,AccountNotFoundError,InsufficientFundsError,InactiveAccountError
from src.utils.file_manager import read_user_transactions

def user_menu():
    """Create a new account with PIN setup"""
    bank = BankingService()
    
    try:
        print("\n---- Create New Account ----")
        name = input("Enter your name: ")
        age = input("Enter your age: ")
        account_type = input("Enter account type (Savings/Current): ")
        initial_deposit = input("Enter initial deposit amount: ")
        
        # Create account
        acc, msg = bank.create_account(name, age, account_type, initial_deposit, timestamp=time.strftime("%Y-%m-%d %H:%M:%S"))
        if acc:
            print(f"Account created successfully! Your account number is {acc.account_number}")
            
            # Set up PIN for the new account
            while True:
                pin = input("Set your 4-digit PIN: ")
                if len(pin) == 4 and pin.isdigit():
                    bank.set_pin(acc.account_number, pin)
                    print("PIN set successfully!")
                    break
                else:
                    print("PIN must be exactly 4 digits. Please try again.")
            
            print("\nAccount setup complete! Redirecting to main menu...")
            time.sleep(2)
            
            # Redirect to main menu
            import main
            main.user_menu(acc.account_number)
        else:
            print(f"Failed to create account: {msg}")
            
    except AgeRestrictionError as e:
        print(f"Failed to create account: {e.message} (Provided age: {e.age})")

    except Exception as e:
        print(f"Error: {str(e)}")