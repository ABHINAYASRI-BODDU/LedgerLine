
from sqlalchemy import text
from sqlalchemy.engine import Engine


def install_ledger_immutability_triggers(engine: Engine) -> None:
    """
    Prevent updates and deletions of ledger entries.
    Supports both SQLite and PostgreSQL.
    """

    database_type = engine.dialect.name

    with engine.begin() as connection:

        if database_type == "sqlite":

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

        elif database_type == "postgresql":

            connection.execute(text("""
                CREATE OR REPLACE FUNCTION prevent_ledger_entry_mutation()
                RETURNS TRIGGER AS $$
                BEGIN
                    RAISE EXCEPTION 'Ledger entries are immutable';
                END;
                $$ LANGUAGE plpgsql;
            """))

            connection.execute(text("""
                DROP TRIGGER IF EXISTS prevent_ledger_entry_update
                ON ledger_entries;
            """))

            connection.execute(text("""
                DROP TRIGGER IF EXISTS prevent_ledger_entry_delete
                ON ledger_entries;
            """))

            connection.execute(text("""
                CREATE TRIGGER prevent_ledger_entry_update
                BEFORE UPDATE OR DELETE ON ledger_entries
                FOR EACH ROW
                EXECUTE FUNCTION prevent_ledger_entry_mutation();
            """))

        else:
            raise RuntimeError(
                f"Unsupported database for ledger protection: {database_type}"
            )
