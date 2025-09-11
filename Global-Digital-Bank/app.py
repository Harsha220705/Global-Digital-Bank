import time
import calendar
from datetime import datetime
import streamlit as st

from src.services.banking_service import (
    BankingService,
    AgeRestrictionError,
    AccountNotFoundError,
    InsufficientFundsError,
    InactiveAccountError,
)
from src.services.loan_services import LoanService
from src.utils.file_manager import read_user_transactions, read_admin_actions, USER_TRANSACTIONS_FILE


st.set_page_config(page_title="Global Digital Bank", page_icon="💳", layout="centered")


def ensure_session_state():
    if "bank" not in st.session_state:
        st.session_state.bank = BankingService()
    if "loan" not in st.session_state:
        st.session_state.loan = LoanService()
    if "role" not in st.session_state:
        st.session_state.role = None  # "user" | "admin"
    if "account_number" not in st.session_state:
        st.session_state.account_number = None


def login_view():
    st.title("Global Digital Bank")
    st.subheader("Login")
    role = st.radio("Login as", ["User", "Admin"], horizontal=True)

    if role == "User":
        acc_no = st.text_input("Account Number")
        pin = st.text_input("PIN", type="password")
        if st.button("Login"):
            try:
                if not acc_no.strip():
                    st.error("Enter account number")
                    return
                if st.session_state.bank.verify_pin(acc_no, pin):
                    st.session_state.role = "user"
                    st.session_state.account_number = acc_no
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error("Invalid PIN")
            except AccountNotFoundError as e:
                st.error(str(e))

        st.divider()
        st.caption("New here? Create an account")
        with st.form("create_account"):
            name = st.text_input("Name")
            age = st.text_input("Age")
            acc_type = st.selectbox("Account Type", ["Savings", "Current"])
            initial = st.text_input("Initial Deposit")
            pin_new = st.text_input("Set 4-digit PIN", type="password")
            submitted = st.form_submit_button("Create Account")
            if submitted:
                try:
                    if len(pin_new) != 4 or not pin_new.isdigit():
                        st.error("PIN must be exactly 4 digits")
                    else:
                        acc, msg = st.session_state.bank.create_account(
                            name, age, acc_type, initial, timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        )
                        if acc:
                            st.session_state.bank.set_pin(acc.account_number, pin_new)
                            st.success(f"Account created: {acc.account_number}")
                            # Auto-login and redirect to user dashboard
                            st.session_state.role = "user"
                            st.session_state.account_number = str(acc.account_number)
                            st.rerun()
                        else:
                            st.error(msg)
                except AgeRestrictionError as e:
                    st.error(f"{e.message} (Provided age: {e.age})")
                except Exception as e:
                    st.error(str(e))

    else:  # Admin
        key = st.text_input("Security Key", type="password")
        if st.button("Login as Admin"):
            if key == "admin123":
                st.session_state.role = "admin"
                st.success("Admin login successful")
                st.rerun()
            else:
                st.error("Access denied. Wrong key.")


def user_dashboard():
    bank: BankingService = st.session_state.bank
    loan: LoanService = st.session_state.loan
    acc_no = st.session_state.account_number
    try:
        acc = bank.get_account(acc_no)
    except Exception:
        acc = None

    st.sidebar.title("User Menu")
    # UI font size tweaks
    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"] { font-size: 18px; }
        [data-testid="stSidebar"] { font-size: 18px; }
        h1, h2, h3 { letter-spacing: 0.2px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    choice = st.sidebar.radio(
        "",
        [
            "Balance",
            "Deposit",
            "Withdraw",
            "Transfer",
            "Insights",
            "Monthly Analytics",
            "Rename",
            "Upgrade Type",
            "Reopen Account",
            "Close Account",
            "Loan - Take",
            "Loan - Details",
            "Logout",
        ],
    )

    st.title("Welcome to Global Digital Bank")
    if acc:
        st.info(f"[{acc.account_number}] {acc.name} • {acc.account_type} • Balance: {acc.balance}")

    if choice == "Balance":
        try:
            acc, msg = bank.balance_inquiry(acc_no)
            if acc:
                st.success(msg)
        except AccountNotFoundError as e:
            st.error(str(e))

    elif choice == "Deposit":
        amount = st.text_input("Amount")
        loan_repay = st.checkbox("This is for Loan Repayment")
        if st.button("Deposit"):
            try:
                amt = float(amount)
                if loan_repay:
                    ok_r, msg_r, applied = loan.repay(int(acc_no), amt)
                    st.info(msg_r)
                    remainder = round(amt - applied, 2)
                    if remainder > 0:
                        ok, msg = bank.deposit(acc_no, remainder)
                        st.success(msg)
                else:
                    ok, msg = bank.deposit(acc_no, amt)
                    st.success(msg)
            except ValueError:
                st.error("Invalid amount")
            except AccountNotFoundError as e:
                st.error(f"Deposit failed: Account {e.account_number} not found.")
            except InactiveAccountError as e:
                st.error(str(e))
            except Exception as e:
                st.error(str(e))

    elif choice == "Withdraw":
        amount = st.text_input("Amount")
        if st.button("Withdraw"):
            try:
                ok, msg = bank.withdraw(acc_no, amount)
                (st.success if ok else st.error)(msg)
            except ValueError:
                st.error("Invalid amount")
            except AccountNotFoundError as e:
                st.error(f"Withdrawal failed: Account {e.account_number} not found.")
            except InactiveAccountError as e:
                st.error(str(e))
            except InsufficientFundsError as e:
                st.error(str(e))
            except Exception as e:
                st.error(str(e))

    elif choice == "Transfer":
        to_acc = st.text_input("To Account")
        amount = st.text_input("Amount")
        if st.button("Transfer"):
            try:
                recv = bank.get_account(to_acc)
                if not recv:
                    st.error("Receiver account not found.")
                else:
                    ok, msg = bank.transfer_funds(acc_no, to_acc, amount)
                    (st.success if ok else st.error)(msg)
            except Exception as e:
                st.error(str(e))

    elif choice == "Insights":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Simple Interest")
            years = st.text_input("Years", key="si_years")
            if st.button("Calculate", key="si_calc_btn"):
                try:
                    acc = bank.get_account(acc_no)
                    rate = "7.5" if acc.account_type == "Savings" else "9.5"
                    ok, msg = bank.calculate_simple_interest(acc_no, rate, years)
                    (st.success if ok else st.error)(msg)
                except Exception as e:
                    st.error(str(e))
        with col2:
            st.subheader("Daily Limits")
            try:
                dep_used = bank._get_today_total(int(acc_no), "DEPOSIT")
                wit_used = bank._get_today_total(int(acc_no), "WITHDRAW")
                st.metric("Deposit remaining today", f"{bank.DAILY_DEPOSIT_LIMIT - dep_used:.2f}")
                st.metric("Withdraw remaining today", f"{bank.DAILY_WITHDRAW_LIMIT - wit_used:.2f}")
            except Exception:
                st.error("Could not compute daily limits.")

    elif choice == "Monthly Analytics":
        st.subheader("This Month's Transactions")
        # Build per-day totals for deposits and withdrawals separately
        try:
            now = datetime.now()
            month_prefix = now.strftime("%Y-%m-")  # e.g., 2025-09-
            days_in_month = calendar.monthrange(now.year, now.month)[1]
            dep_by_day = {day: 0.0 for day in range(1, days_in_month + 1)}
            wit_by_day = {day: 0.0 for day in range(1, days_in_month + 1)}
            try:
                with open(USER_TRANSACTIONS_FILE, "r") as f:
                    for line in f:
                        if not line.startswith(month_prefix):
                            continue
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) < 4:
                            continue
                        try:
                            log_date = parts[0]  # YYYY-MM-DD ...
                            log_day = int(log_date.split(" ")[0].split("-")[-1])
                            log_acc = int(parts[1])
                            op = parts[2]
                            amt = float(parts[3]) if parts[3] != "None" else 0.0
                        except Exception:
                            continue
                        if str(log_acc) != str(acc_no):
                            continue
                        if op in ("DEPOSIT", "TRANSFER_IN", "LOAN_CREDIT"):
                            dep_by_day[log_day] += amt
                        elif op in ("WITHDRAW", "WITHDRAW_FULL", "TRANSFER_OUT"):
                            wit_by_day[log_day] += amt
            except FileNotFoundError:
                pass

            import pandas as pd
            import altair as alt
            days = list(range(1, days_in_month + 1))
            df_dep = pd.DataFrame({"day": days, "amount": [dep_by_day[d] for d in days], "kind": "Deposit"})
            df_wit = pd.DataFrame({"day": days, "amount": [wit_by_day[d] for d in days], "kind": "Withdraw"})
            df = pd.concat([df_dep, df_wit], ignore_index=True)

            color_scale = alt.Scale(domain=["Deposit", "Withdraw"], range=["#1f77b4", "#d62728"])  # blue, red
            chart = (
                alt.Chart(df)
                .mark_bar()
                .encode(
                    x=alt.X("day:O", title="Day of Month"),
                    y=alt.Y("amount:Q", title="Amount (₹)"),
                    color=alt.Color("kind:N", scale=color_scale, legend=alt.Legend(title="Type")),
                    tooltip=["day", "kind", "amount"],
                )
                .properties(width=700, height=300)
            )
            st.altair_chart(chart, use_container_width=True)
        except Exception as e:
            st.error(f"Could not render analytics: {str(e)}")

    elif choice == "Rename":
        new_name = st.text_input("New Name")
        if st.button("Rename"):
            try:
                # account_rename prompts in CLI; here we directly set
                acc = bank.get_account(acc_no)
                if not new_name.strip():
                    st.error("Name cannot be empty")
                else:
                    acc.name = new_name.strip()
                    bank.save_to_disk()
                    st.success(f"Renamed to {new_name}")
            except Exception as e:
                st.error(str(e))

    elif choice == "Upgrade Type":
        new_type = st.selectbox("New Type", ["Savings", "Current"])
        if st.button("Upgrade"):
            ok, msg = st.session_state.bank.upgrade_account_type(acc_no, new_type)
            (st.success if ok else st.error)(msg)

    elif choice == "Reopen Account":
        if st.button("Reopen"):
            ok, msg = st.session_state.bank.reopen_account(acc_no)
            (st.success if ok else st.error)(msg)

    elif choice == "Close Account":
        if st.button("Close Now"):
            try:
                ok, msg = st.session_state.bank.terminate_account(acc_no)
                (st.success if ok else st.error)(msg)
            except Exception as e:
                st.error(str(e))

    elif choice == "Loan - Take":
        if not acc:
            st.error("Account not found")
        else:
            st.write(
                f"Eligible limit for {acc.account_type}: ₹{LoanService.get_max_limit_for_account_type(acc.account_type):,.0f}"
            )
            amount = st.text_input("Loan Amount")
            years = st.selectbox("Tenure (years)", [3, 4])
            if st.button("Submit Application"):
                try:
                    ok, msg, app = st.session_state.loan.submit_application(acc, float(amount), int(years))
                    (st.success if ok else st.error)(msg)
                except Exception as e:
                    st.error(str(e))

    elif choice == "Loan - Details":
        try:
            loan_details = st.session_state.loan.details(int(acc_no))
            if loan_details == "No Loan Taken.":
                st.info("No Loan Taken.")
            else:
                st.subheader("📊 Loan Details")
                st.code(loan_details, language="text")
        except Exception as e:
            st.error(str(e))

    elif choice == "Logout":
        st.session_state.role = None
        st.session_state.account_number = None
        st.rerun()


def admin_dashboard():
    bank: BankingService = st.session_state.bank
    loan: LoanService = st.session_state.loan
    st.sidebar.title("Admin Menu")
    choice = st.sidebar.radio(
        "",
        [
            "Active Accounts",
            "Closed Accounts",
            "Logs",
            "Search by Account",
            "Transaction History",
            "Top Age Extremes (Top 3)",
            "Top N by Balance",
            "Summary",
            "System Exit (Autosave)",
            "Logout",
        ],
    )

    st.title("Admin Dashboard")

    if choice == "Active Accounts":
        st.text(st.session_state.bank.save_to_disk() or "")
        st.write("Listing active accounts:")
        q = st.text_input("Search by name or account number")
        for acc in bank.accounts.values():
            if acc.status != "Active":
                continue
            row = f"{acc.account_number} | {acc.name} | Balance: {acc.balance}"
            if q and q.strip():
                if q.strip().lower() not in row.lower():
                    continue
            st.code(row)

    elif choice == "Closed Accounts":
        for acc in bank.accounts.values():
            if acc.status != "Active":
                st.code(f"{acc.account_number} | {acc.name} | Balance: {acc.balance} | {acc.status}")

    elif choice == "Logs":
        q = st.text_input("Filter by account number (optional)")
        logs = read_user_transactions() or ""
        actions = read_admin_actions() or ""
        if q.strip():
            try:
                qnum = str(int(q.strip()))
            except Exception:
                qnum = None
            if qnum:
                logs = "\n".join([line for line in logs.splitlines() if f"| {qnum} |" in line])
        if logs.strip():
            st.subheader("User Transactions")
            st.code(logs)
        if actions.strip():
            st.subheader("Admin Actions")
            st.code(actions)
        if not (logs.strip() or actions.strip()):
            st.info("No logs found.")

    elif choice == "Search by Account":
        acc_no = st.text_input("Account Number")
        if st.button("Search"):
            try:
                acc = bank.get_account(acc_no)
                if not acc:
                    st.warning("Not found")
                else:
                    st.write(f"{acc.account_number} | {acc.name} | {acc.age} | {acc.account_type} | Bal: {acc.balance}")
            except Exception as e:
                st.error(str(e))

    elif choice == "Transaction History":
        acc_no = st.text_input("Account Number")
        if st.button("View History"):
            try:
                st.code(bank.transaction_history(acc_no))
            except Exception as e:
                st.error(str(e))

    elif choice == "Top Age Extremes (Top 3)":
        if not bank.accounts:
            st.info("No accounts.")
        else:
            youngest = sorted([a for a in bank.accounts.values()], key=lambda x: x.age)[:3]
            oldest = sorted([a for a in bank.accounts.values()], key=lambda x: x.age, reverse=True)[:3]
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Top 3 Youngest")
                for a in youngest:
                    st.code(f"{a.account_number} | {a.name} | Age: {a.age}")
            with col2:
                st.subheader("Top 3 Oldest")
                for a in oldest:
                    st.code(f"{a.account_number} | {a.name} | Age: {a.age}")

    elif choice == "Top N by Balance":
        n = st.text_input("N")
        if st.button("Show Top N"):
            try:
                top = bank.top_n_accounts_by_balance(n)
                if not top:
                    st.info("No accounts or invalid N.")
                else:
                    for a in top:
                        st.code(f"{a.account_number} | {a.name} | Balance: {a.balance}")
            except Exception as e:
                st.error(str(e))

    elif choice == "Summary":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Balance", f"{bank.average_balance():.2f}")
        with col2:
            cnt = sum(1 for a in bank.accounts.values() if a.status == "Active")
            st.metric("Active Accounts", f"{cnt}")
        with col3:
            active = loan.get_active_loans_list()
            st.metric("Active Loans", f"{len(active)}")
        if active:
            st.subheader("Active Loans (Acc | Name)")
            for acc_no, name in active:
                st.code(f"{acc_no} | {name}")
        # Pending Applications section (admin approval)
        st.subheader("Pending Loan Applications")
        apps = loan.list_applications()
        if not apps:
            st.info("No pending applications.")
        else:
            # Inline actions for each application
            for app in apps:
                st.code(
                    f"{app['account_number']} | {app['name']} | ₹{app['principal']:,.0f} | {app['years']} years | {app['requested_at']}"
                )
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    rate_input = st.text_input(
                        f"Rate % for {app['account_number']}", value="6.0", key=f"rate_{app['account_number']}"
                    )
                with c2:
                    if st.button("Approve", key=f"approve_{app['account_number']}"):
                        try:
                            account = bank.get_account(app["account_number"])
                            if not account:
                                st.error("Account not found.")
                            else:
                                ok, msg, record = loan.approve_application(account, float(rate_input)/100.0)
                                (st.success if ok else st.error)(msg)
                                if ok and record:
                                    okd, msgd = bank.credit_loan_disbursal(app["account_number"], record["principal"])
                                    st.success(f"Disbursed: {msgd}")
                                    st.rerun()
                        except Exception as e:
                            st.error(str(e))
                with c3:
                    if st.button("Reject", key=f"reject_{app['account_number']}"):
                        ok, msg, _ = loan.reject_application(app["account_number"])
                        (st.success if ok else st.error)(msg)
                        st.rerun()

    elif choice == "System Exit (Autosave)":
        bank.save_to_disk()
        st.success("System state saved.")

    elif choice == "Logout":
        st.session_state.role = None
        st.rerun()


def main():
    ensure_session_state()
    if st.session_state.role == "user":
        user_dashboard()
    elif st.session_state.role == "admin":
        admin_dashboard()
    else:
        login_view()


if __name__ == "__main__":
    main()


