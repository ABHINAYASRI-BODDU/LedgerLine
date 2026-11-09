from sqlalchemy import text
from sqlalchemy.engine import Engine


def install_ledger_immutability_triggers(engine: Engine) -> None:
    """
    Prevent updates and deletions of ledger entries.
    """

    with engine.begin() as connection:

        connection.execute(text("""
            CREATE TRIGGER IF NOT EXISTS prevent_ledger_entry_update
            BEFORE UPDATE ON ledger_entries
            BEGIN
                SELECT RAISE(ABORT, 'Ledger entries are immutable');
            END;
        """))

        connection.execute(text("""
            CREATE TRIGGER IF NOT EXISTS prevent_ledger_entry_delete
            BEFORE DELETE ON ledger_entries
            BEGIN
                SELECT RAISE(ABORT, 'Ledger entries are immutable');
            END;
        """))