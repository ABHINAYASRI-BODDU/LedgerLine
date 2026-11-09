from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction
from app.models.ledger_entry import LedgerEntry


def verify_ledger_integrity(db: Session):
    """
    Verify the integrity of all posted transactions.

    Checks:
    1. Every posted transaction has ledger entries.
    2. Debit total equals credit total.
    3. Both totals equal the transaction amount.
    """

    posted_transactions = (
        db.query(Transaction)
        .filter(Transaction.status == "posted")
        .order_by(Transaction.id)
        .all()
    )

    checked_transactions = 0
    invalid_transactions = []

    for transaction in posted_transactions:

        debit_total = (
            db.query(func.sum(LedgerEntry.amount_paise))
            .filter(
                LedgerEntry.transaction_id == transaction.id,
                LedgerEntry.entry_type == "debit"
            )
            .scalar() or 0
        )

        credit_total = (
            db.query(func.sum(LedgerEntry.amount_paise))
            .filter(
                LedgerEntry.transaction_id == transaction.id,
                LedgerEntry.entry_type == "credit"
            )
            .scalar() or 0
        )

        checked_transactions += 1

        if (
            debit_total != credit_total
            or debit_total != transaction.amount_paise
            or credit_total != transaction.amount_paise
        ):
            invalid_transactions.append({
                "transaction_id": transaction.id,
                "transaction_amount_paise": transaction.amount_paise,
                "debit_total_paise": debit_total,
                "credit_total_paise": credit_total,
                "reason": (
                    "Missing ledger entries or transaction is unbalanced."
                )
            })

    return {
        "is_valid": len(invalid_transactions) == 0,
        "checked_transactions": checked_transactions,
        "invalid_transactions": invalid_transactions
    }