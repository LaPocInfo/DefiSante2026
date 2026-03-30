"""Run safe ALTER TABLE migrations on startup for columns added after initial deploy."""
from sqlalchemy import text


def run_migrations(db):
    migrations = [
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='saisie_activite' AND column_name='intensite'
          ) THEN
            ALTER TABLE saisie_activite ADD COLUMN intensite VARCHAR(20) DEFAULT 'moyenne';
          END IF;
        END $$;
        """,
    ]
    with db.engine.connect() as conn:
        for sql in migrations:
            conn.execute(text(sql))
        conn.commit()
    print("✅ Migrations OK")
