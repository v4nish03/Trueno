import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

# ✅ Base de datos EN MEMORIA para tests (no afecta la real)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Crea una sesión de base de datos para cada test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de pruebas con base de datos en memoria"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def producto_ejemplo(client):
    """Crea un producto de ejemplo para los tests"""
    response = client.post("/productos/", json={
        "codigo": "TEST001",
        "nombre": "Producto Test",
        "descripcion": "Descripción de prueba",
        "precio1": 100.0,
        "precio2": 95.0,
        "precio3": 90.0,
        "precio4": 85.0,
        "stock_inicial": 50,
        "stock_minimo": 10,
        "ubicacion": "tienda"
    })
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def producto_sin_stock(client):
    """Crea un producto SIN stock para tests"""
    response = client.post("/productos/", json={
        "codigo": "SIN_STOCK",
        "nombre": "Producto Sin Stock",
        "precio1": 50.0,
        "stock_inicial": 0,
        "stock_minimo": 5
    })
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def venta_abierta(client, producto_ejemplo):
    """Crea una venta abierta con un producto"""
    # Abrir venta
    response = client.post("/ventas/abrir")
    assert response.status_code == 200
    venta = response.json()
    
    # Agregar producto
    client.post(
        f"/ventas/{venta['venta_id']}/productos",
        json={
            "producto_id": producto_ejemplo["id"],
            "cantidad": 5,
            "precio_unitario": producto_ejemplo["precio1"]
        }
    )
    
    return venta


@pytest.fixture
def venta_completa(client, venta_abierta):
    """Crea una venta completa y cerrada"""
    response = client.post(
        f"/ventas/{venta_abierta['venta_id']}/cerrar",
        json={"metodo_pago": "efectivo"}
    )
    assert response.status_code == 200
    return response.json()