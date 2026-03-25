from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def asegurar_columnas_catalogo(engine: Engine):
    """
    Migración liviana y segura para entornos sin Alembic.
    Agrega columnas nuevas sin tocar datos existentes.
    """
    inspector = inspect(engine)
    tablas = inspector.get_table_names()
    if "productos" not in tablas:
        return

    columnas = {col["name"] for col in inspector.get_columns("productos")}
    pendientes = []

    if "categoria" not in columnas:
        pendientes.append("ALTER TABLE productos ADD COLUMN categoria VARCHAR(80)")

    if "imagen_url" not in columnas:
        pendientes.append("ALTER TABLE productos ADD COLUMN imagen_url TEXT")

    if "stock_bodega" not in columnas:
        pendientes.append("ALTER TABLE productos ADD COLUMN stock_bodega INTEGER NOT NULL DEFAULT 0")

    with engine.begin() as conn:
        for sentencia in pendientes:
            conn.execute(text(sentencia))

        # PostgreSQL: asegurar nuevo valor del enum de movimientos
        if engine.dialect.name == "postgresql":
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_enum e
                        JOIN pg_type t ON t.oid = e.enumtypid
                        WHERE t.typname = 'motivomovimientoenum'
                          AND e.enumlabel = 'traslado_bodega_tienda'
                    ) THEN
                        ALTER TYPE motivomovimientoenum ADD VALUE 'traslado_bodega_tienda';
                    END IF;
                END
                $$;
            """))
