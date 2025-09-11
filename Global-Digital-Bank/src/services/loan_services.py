import csv
import os
from typing import Dict, Optional, Tuple


BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
LOANS_FILE = os.path.join(BASE_DATA_DIR, "loans.csv")
APPLICATIONS_FILE = os.path.join(BASE_DATA_DIR, "loan_applications.csv")


class LoanService:
    """Manages loans with simple-interest EMI.

    - One active loan per account.
    - Total payable = principal + principal * rate * years
    - EMI = total_payable / (years * 12)
    """

    def __init__(self) -> None:
        self.loans: Dict[int, Dict] = self._load_loans()
        self.applications: Dict[int, Dict] = self._load_applications()

    def _load_loans(self) -> Dict[int, Dict]:
        loans: Dict[int, Dict] = {}
        try:
            with open(LOANS_FILE, mode="r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        acc = int(row.get("account_number", "0") or 0)
                    except ValueError:
                        continue
                    loans[acc] = {
                        "account_number": acc,
                        "name": row.get("name", "").strip(),
                        "principal": float(row.get("principal", "0") or 0.0),
                        "pending": float(row.get("pending", "0") or 0.0),
                        "years": int(row.get("years", "0") or 0),
                        "rate": float(row.get("rate", "0") or 0.0),
                        "status": row.get("status", "None").strip() or "None",
                    }
        except FileNotFoundError:
            # create directory if needed
            os.makedirs(os.path.dirname(LOANS_FILE), exist_ok=True)
        return loans

    def _save_loans(self) -> None:
        os.makedirs(os.path.dirname(LOANS_FILE), exist_ok=True)
        with open(LOANS_FILE, mode="w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "account_number",
                    "name",
                    "principal",
                    "pending",
                    "years",
                    "rate",
                    "status",
                ],
            )
            writer.writeheader()
            for loan in self.loans.values():
                writer.writerow(
                    {
                        "account_number": loan["account_number"],
                        "name": loan.get("name", ""),
                        "principal": loan.get("principal", 0.0),
                        "pending": loan.get("pending", 0.0),
                        "years": loan.get("years", 0),
                        "rate": loan.get("rate", 0.0),
                        "status": loan.get("status", "None"),
                    }
                )

    def _load_applications(self) -> Dict[int, Dict]:
        apps: Dict[int, Dict] = {}
        try:
            with open(APPLICATIONS_FILE, mode="r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        acc = int(row.get("account_number", "0") or 0)
                    except ValueError:
                        continue
                    apps[acc] = {
                        "account_number": acc,
                        "name": row.get("name", "").strip(),
                        "principal": float(row.get("principal", "0") or 0.0),
                        "years": int(row.get("years", "0") or 0),
                        "requested_at": row.get("requested_at", "") or "",
                    }
        except FileNotFoundError:
            os.makedirs(os.path.dirname(APPLICATIONS_FILE), exist_ok=True)
        return apps

    def _save_applications(self) -> None:
        os.makedirs(os.path.dirname(APPLICATIONS_FILE), exist_ok=True)
        with open(APPLICATIONS_FILE, mode="w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "account_number",
                    "name",
                    "principal",
                    "years",
                    "requested_at",
                ],
            )
            writer.writeheader()
            for app in self.applications.values():
                writer.writerow(
                    {
                        "account_number": app["account_number"],
                        "name": app.get("name", ""),
                        "principal": app.get("principal", 0.0),
                        "years": app.get("years", 0),
                        "requested_at": app.get("requested_at", ""),
                    }
                )

    @staticmethod
    def get_rate_for_account_type(account_type: str) -> float:
        at = (account_type or "").strip().title()
        if at == "Savings":
            return 0.06  # 6%
        if at == "Current":
            return 0.08  # 8%
        return 0.06

    @staticmethod
    def get_max_limit_for_account_type(account_type: str) -> float:
        at = (account_type or "").strip().title()
        if at == "Savings":
            return 1000000.0
        if at == "Current":
            return 2500000.0
        return 0.0

    @staticmethod
    def compute_total_payable(principal: float, years: int, rate: float) -> float:
        # Simple interest total = P + P*r*t
        return round(float(principal) * (1.0 + float(rate) * int(years)), 2)

    @staticmethod
    def compute_emi(total_payable: float, years: int) -> float:
        months = int(years) * 12
        if months <= 0:
            return 0.0
        return round(float(total_payable) / months, 2)

    def get(self, account_number: int) -> Optional[Dict]:
        try:
            return self.loans.get(int(account_number))
        except Exception:
            return None

    def get_active_loans_list(self):
        return [
            (acc, loan.get("name", ""))
            for acc, loan in self.loans.items()
            if loan.get("pending", 0.0) > 0 and loan.get("status", "None") != "Cleared"
        ]

    # -------- Applications Flow --------
    def submit_application(self, account, amount: float, years: int) -> tuple:
        try:
            acc_no = int(account.account_number)
        except Exception:
            return False, "Invalid account.", None
        if years not in (3, 4):
            return False, "Loan tenure must be 3 or 4 years.", None
        amount_f = float(amount)
        if amount_f <= 0:
            return False, "Loan amount must be positive.", None
        # Can't apply if active loan exists
        existing = self.get(acc_no)
        if existing and existing.get("pending", 0.0) > 0 and existing.get("status") != "Cleared":
            return False, "Active loan exists. Please clear it first.", None
        # Save/replace application
        from datetime import datetime as dt
        self.applications[acc_no] = {
            "account_number": acc_no,
            "name": account.name,
            "principal": amount_f,
            "years": int(years),
            "requested_at": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self._save_applications()
        return True, "Loan application submitted.", self.applications[acc_no]

    def list_applications(self):
        # returns list of dicts
        return list(self.applications.values())

    def reject_application(self, account_number: int) -> tuple:
        try:
            acc_no = int(account_number)
        except Exception:
            return False, "Invalid account.", None
        app = self.applications.get(acc_no)
        if not app:
            return False, "No application found for this account.", None
        del self.applications[acc_no]
        self._save_applications()
        return True, "Application rejected and removed.", None

    def approve_application(self, account, custom_rate: float) -> tuple:
        try:
            acc_no = int(account.account_number)
        except Exception:
            return False, "Invalid account.", None
        app = self.applications.get(acc_no)
        if not app:
            return False, "No application found for this account.", None
        amount_f = float(app["principal"])
        years = int(app["years"])
        # enforce max limit
        max_limit = self.get_max_limit_for_account_type(account.account_type)
        if amount_f > max_limit:
            return False, f"Loan exceeds limit of ₹{max_limit:,.0f} for {account.account_type}.", None
        rate = float(custom_rate)
        if rate <= 0:
            return False, "Rate must be positive.", None
        total_payable = self.compute_total_payable(amount_f, years, rate)
        record = {
            "account_number": acc_no,
            "name": account.name,
            "principal": amount_f,
            "pending": total_payable,
            "years": int(years),
            "rate": rate,
            "status": "Active",
        }
        self.loans[acc_no] = record
        # delete application
        if acc_no in self.applications:
            del self.applications[acc_no]
            self._save_applications()
        self._save_loans()
        return True, (
            f"Application approved. Loan: ₹{amount_f:,.0f} for {years} years at {rate*100:.1f}%. "
            f"Total payable: ₹{total_payable:,.0f}."
        ), record

    def take_loan(self, account, amount: float, years: int) -> Tuple[bool, str, Optional[Dict]]:
        """Sanction a loan and record it. Does NOT credit funds; caller should deposit principal.

        Returns (ok, msg, loan_record_or_none)
        """
        try:
            acc_no = int(account.account_number)
        except Exception:
            return False, "Invalid account.", None

        existing = self.get(acc_no)
        if existing and existing.get("pending", 0.0) > 0 and existing.get("status") != "Cleared":
            return False, "Active loan exists. Please clear it first.", None

        amount_f = float(amount)
        if amount_f <= 0:
            return False, "Loan amount must be positive.", None
        if years not in (3, 4):
            return False, "Loan tenure must be 3 or 4 years.", None

        max_limit = self.get_max_limit_for_account_type(account.account_type)
        if amount_f > max_limit:
            return False, f"Loan exceeds limit of ₹{max_limit:,.0f} for {account.account_type}.", None

        rate = self.get_rate_for_account_type(account.account_type)
        total_payable = self.compute_total_payable(amount_f, years, rate)

        record = {
            "account_number": acc_no,
            "name": account.name,
            "principal": amount_f,
            "pending": total_payable,
            "years": int(years),
            "rate": rate,
            "status": "Active",
        }
        self.loans[acc_no] = record
        self._save_loans()

        return True, (
            f"Loan sanctioned: ₹{amount_f:,.0f} for {years} years at {int(rate*100)}%. "
            f"Total payable: ₹{total_payable:,.0f}."
        ), record

    def repay(self, account_number: int, amount: float) -> Tuple[bool, str, float]:
        """Apply repayment to loan. Returns (ok, msg, applied_amount)."""
        loan = self.get(account_number)
        if not loan or loan.get("pending", 0.0) <= 0:
            return False, "No active loan to repay.", 0.0
        amt = max(0.0, float(amount))
        if amt <= 0:
            return False, "Repayment must be positive.", 0.0

        pending = float(loan.get("pending", 0.0))
        applied = min(amt, pending)
        new_pending = round(pending - applied, 2)
        loan["pending"] = new_pending
        if new_pending <= 0:
            loan["pending"] = 0.0
            loan["status"] = "Cleared"
        self._save_loans()

        if loan["status"] == "Cleared":
            return True, "Loan Cleared Successfully.", applied
        return True, f"Repayment applied. Pending: ₹{loan['pending']:,.0f}", applied

    def details(self, account_number: int) -> str:
        loan = self.get(account_number)
        if not loan:
            return "No Loan Taken."
        principal = loan.get("principal", 0.0)
        pending = loan.get("pending", 0.0)
        years = loan.get("years", 0)
        rate = loan.get("rate", 0.0)
        # Compute EMIs for both tenures for display
        total3 = self.compute_total_payable(principal, 3, rate)
        emi3 = self.compute_emi(total3, 3)
        total4 = self.compute_total_payable(principal, 4, rate)
        emi4 = self.compute_emi(total4, 4)
        status = loan.get("status", "Active")
        return (
            f"Loan Amount sanctioned: ₹{principal:,.0f}\n"
            f"Loan Amount pending: ₹{pending:,.0f}\n"
            f"EMI per month (3 years): ₹{emi3:,.2f}\n"
            f"EMI per month (4 years): ₹{emi4:,.2f}\n"
            f"Repayment status: {status}"
        )


