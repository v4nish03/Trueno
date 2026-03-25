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

    if not pendientes:
        return

    with engine.begin() as conn:
        for sentencia in pendientes:
            conn.execute(text(sentencia))
