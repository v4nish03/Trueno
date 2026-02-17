import pytest


class TestCrearProducto:
    """Tests para crear productos"""

    def test_crear_producto_completo(self, client):
        """Debería crear un producto con todos los datos"""
        response = client.post("/productos/", json={
            "codigo": "PROD001",
            "nombre": "Aceite 10W40",
            "descripcion": "Aceite sintético",
            "precio1": 85.50,
            "precio2": 80.0,
            "precio3": 75.0,
            "precio4": 70.0,
            "stock_inicial": 100,
            "stock_minimo": 15,
            "ubicacion": "bodega"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["codigo"] == "PROD001"
        assert data["nombre"] == "Aceite 10W40"
        assert data["stock"] == 100
        assert data["activo"] is True

    def test_crear_producto_minimo(self, client):
        """Debería crear un producto con datos mínimos"""
        response = client.post("/productos/", json={
            "codigo": "MIN001",
            "nombre": "Producto Mínimo",
            "precio1": 50.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["stock"] == 0
        assert data["stock_minimo"] == 5

    def test_crear_producto_codigo_duplicado(self, client, producto_ejemplo):
        """NO debería permitir códigos duplicados"""
        response = client.post("/productos/", json={
            "codigo": producto_ejemplo["codigo"],
            "nombre": "Otro producto",
            "precio1": 100.0
        })
        
        assert response.status_code == 400
        assert "Ya existe un producto" in response.json()["detail"]




    def test_no_crear_producto_con_precio_invalido(self, client):
        """No debería permitir precio <= 0"""
        response = client.post("/productos/", json={
            "codigo": "BADPRICE",
            "nombre": "Producto Inválido",
            "precio1": 0
        })

        assert response.status_code == 422

    def test_no_crear_producto_con_ubicacion_invalida(self, client):
        """No debería permitir ubicaciones fuera de tienda/bodega"""
        response = client.post("/productos/", json={
            "codigo": "BADLOC",
            "nombre": "Ubicación Inválida",
            "precio1": 10.0,
            "ubicacion": "mostrador"
        })

        assert response.status_code == 400


class TestListarProductos:
    """Tests para listar productos"""

    def test_listar_productos_vacio(self, client):
        """Debería devolver lista vacía si no hay productos"""
        response = client.get("/productos/")
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_productos(self, client, producto_ejemplo):
        """Debería listar productos existentes"""
        response = client.get("/productos/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["codigo"] == producto_ejemplo["codigo"]

    def test_buscar_producto_por_nombre(self, client, producto_ejemplo):
        """Debería buscar productos por nombre"""
        response = client.get("/productos/?buscar=Test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_buscar_producto_por_codigo(self, client, producto_ejemplo):
        """Debería buscar productos por código"""
        response = client.get("/productos/?buscar=TEST")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestObtenerProducto:
    """Tests para obtener producto individual"""

    def test_obtener_producto_por_id(self, client, producto_ejemplo):
        """Debería obtener producto por ID"""
        response = client.get(f"/productos/{producto_ejemplo['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == producto_ejemplo["id"]

    def test_obtener_producto_inexistente(self, client):
        """Debería devolver 404 si no existe"""
        response = client.get("/productos/99999")
        assert response.status_code == 404

    def test_obtener_producto_por_codigo(self, client, producto_ejemplo):
        """Debería obtener producto por código"""
        response = client.get(f"/productos/codigo/{producto_ejemplo['codigo']}")
        assert response.status_code == 200
        data = response.json()
        assert data["codigo"] == producto_ejemplo["codigo"]


class TestActualizarProducto:
    """Tests para actualizar productos"""

    def test_actualizar_nombre_producto(self, client, producto_ejemplo):
        """Debería actualizar el nombre"""
        response = client.put(
            f"/productos/{producto_ejemplo['id']}",
            json={"nombre": "Producto Actualizado"}
        )
        assert response.status_code == 200
        
        # Verificar que cambió
        producto = client.get(f"/productos/{producto_ejemplo['id']}").json()
        assert producto["nombre"] == "Producto Actualizado"

    def test_actualizar_precio(self, client, producto_ejemplo):
        """Debería actualizar precios"""
        response = client.put(
            f"/productos/{producto_ejemplo['id']}",
            json={"precio1": 150.0}
        )
        assert response.status_code == 200


class TestGestionStock:
    """Tests para gestión de stock"""

    def test_ingresar_stock(self, client, producto_ejemplo):
        """Debería ingresar stock correctamente"""
        stock_inicial = producto_ejemplo["stock"]
        
        response = client.post(
            f"/productos/{producto_ejemplo['id']}/ingresar-stock?cantidad=20&motivo=compra"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["stock_nuevo"] == stock_inicial + 20

    def test_ajustar_stock_manual(self, client, producto_ejemplo):
        """Debería ajustar el stock manualmente"""
        response = client.post(
            f"/productos/{producto_ejemplo['id']}/ajustar-stock?nuevo_stock=200"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["stock_nuevo"] == 200

    def test_ver_historial_movimientos(self, client, producto_ejemplo):
        """Debería ver el historial de movimientos"""
        # Hacer algunos movimientos
        client.post(f"/productos/{producto_ejemplo['id']}/ingresar-stock?cantidad=10")
        
        response = client.get(f"/productos/{producto_ejemplo['id']}/historial")
        assert response.status_code == 200
        data = response.json()
        assert "movimientos" in data
        assert len(data["movimientos"]) >= 1


class TestDescontinuarProducto:
    """Tests para descontinuar/reactivar productos"""

    def test_descontinuar_producto(self, client, producto_ejemplo):
        """Debería descontinuar un producto"""
        response = client.delete(f"/productos/{producto_ejemplo['id']}")
        assert response.status_code == 200
        
        # Verificar que quedó inactivo
        producto = client.get(f"/productos/{producto_ejemplo['id']}").json()
        assert producto["activo"] is False

    def test_reactivar_producto(self, client, producto_ejemplo):
        """Debería reactivar un producto descontinuado"""
        # Descontinuar
        client.delete(f"/productos/{producto_ejemplo['id']}")
        
        # Reactivar
        response = client.post(f"/productos/{producto_ejemplo['id']}/reactivar")
        assert response.status_code == 200
        
        # Verificar
        producto = client.get(f"/productos/{producto_ejemplo['id']}").json()
        assert producto["activo"] is True