import pytest


class TestCrearVenta:
    """Tests para crear y gestionar ventas"""

    def test_abrir_venta(self, client):
        """Debería crear una venta en estado abierto"""
        response = client.post("/ventas/abrir")
        assert response.status_code == 200
        data = response.json()
        assert "venta_id" in data
        assert data["estado"] == "abierta"

    def test_agregar_producto_a_venta(self, client, producto_ejemplo):
        """Debería agregar productos a venta abierta"""
        # Abrir venta
        venta = client.post("/ventas/abrir").json()
        
        # Agregar producto
        response = client.post(
            f"/ventas/{venta['venta_id']}/productos",
            json={
                "producto_id": producto_ejemplo["id"],
                "cantidad": 3,
                "precio_unitario": producto_ejemplo["precio1"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["cantidad"] == 3
        assert data["producto_id"] == producto_ejemplo["id"]

    def test_agregar_mismo_producto_suma_cantidad(self, client, producto_ejemplo):
        """Debería sumar cantidad si agregas el mismo producto"""
        venta = client.post("/ventas/abrir").json()
        
        # Agregar primera vez
        client.post(
            f"/ventas/{venta['venta_id']}/productos",
            json={
                "producto_id": producto_ejemplo["id"],
                "cantidad": 2,
                "precio_unitario": 100.0
            }
        )
        
        # Agregar segunda vez (mismo producto)
        response = client.post(
            f"/ventas/{venta['venta_id']}/productos",
            json={
                "producto_id": producto_ejemplo["id"],
                "cantidad": 3,
                "precio_unitario": 100.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["cantidad"] == 5  # 2 + 3




    def test_no_agregar_producto_con_cantidad_invalida(self, client, producto_ejemplo):
        """No debería permitir cantidad <= 0 por validación de schema"""
        venta = client.post("/ventas/abrir").json()

        response = client.post(
            f"/ventas/{venta['venta_id']}/productos",
            json={
                "producto_id": producto_ejemplo["id"],
                "cantidad": 0,
                "precio_unitario": 100.0
            }
        )

        assert response.status_code == 422

    def test_no_agregar_producto_con_precio_invalido(self, client, producto_ejemplo):
        """No debería permitir precio <= 0 por validación de schema"""
        venta = client.post("/ventas/abrir").json()

        response = client.post(
            f"/ventas/{venta['venta_id']}/productos",
            json={
                "producto_id": producto_ejemplo["id"],
                "cantidad": 1,
                "precio_unitario": 0
            }
        )

        assert response.status_code == 422


class TestCerrarVenta:
    """Tests para cerrar ventas"""

    def test_cerrar_venta_con_stock(self, client, venta_abierta, producto_ejemplo):
        """Debería cerrar venta y descontar stock"""
        stock_antes = client.get(f"/productos/{producto_ejemplo['id']}").json()["stock"]
        
        response = client.post(
            f"/ventas/{venta_abierta['venta_id']}/cerrar",
            json={"metodo_pago": "efectivo"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["venta"]["estado"] == "completa"
        assert data["venta"]["tipo"] == "normal"
        assert data["venta"]["total"] > 0
        assert "recibo" in data
        
        # Verificar que se descontó el stock
        stock_despues = client.get(f"/productos/{producto_ejemplo['id']}").json()["stock"]
        assert stock_despues < stock_antes

    def test_cerrar_venta_sin_stock(self, client, producto_sin_stock):
        """Debería detectar venta sin stock"""
        # Abrir venta
        venta = client.post("/ventas/abrir").json()
        
        # Agregar producto sin stock
        client.post(
            f"/ventas/{venta['venta_id']}/productos",
            json={
                "producto_id": producto_sin_stock["id"],
                "cantidad": 10,
                "precio_unitario": 50.0
            }
        )
        
        # Cerrar venta
        response = client.post(
            f"/ventas/{venta['venta_id']}/cerrar",
            json={"metodo_pago": "qr"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["venta"]["tipo"] == "sin_stock"



    def test_no_cerrar_venta_con_metodo_pago_invalido(self, client, venta_abierta):
        """No debería aceptar métodos de pago fuera de efectivo/qr"""
        response = client.post(
            f"/ventas/{venta_abierta['venta_id']}/cerrar",
            json={"metodo_pago": "tarjeta"}
        )

        assert response.status_code == 422

    def test_no_cerrar_venta_sin_productos(self, client):
        """NO debería cerrar venta vacía"""
        venta = client.post("/ventas/abrir").json()
        
        response = client.post(
            f"/ventas/{venta['venta_id']}/cerrar",
            json={"metodo_pago": "efectivo"}
        )
        
        assert response.status_code == 400


class TestGestionVentas:
    """Tests para gestión de ventas"""

    def test_obtener_venta(self, client, venta_completa):
        """Debería obtener detalles de una venta"""
        response = client.get(f"/ventas/{venta_completa['venta']['id']}")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["estado"] == "completa"

    def test_listar_ventas(self, client, venta_completa):
        """Debería listar todas las ventas"""
        response = client.get("/ventas/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_eliminar_producto_de_venta_abierta(self, client, producto_ejemplo):
        """Debería eliminar productos de venta abierta"""
        # Crear venta y agregar producto
        venta = client.post("/ventas/abrir").json()
        client.post(
            f"/ventas/{venta['venta_id']}/productos",
            json={
                "producto_id": producto_ejemplo["id"],
                "cantidad": 5,
                "precio_unitario": 100.0
            }
        )
        
        # Eliminar producto
        response = client.delete(
            f"/ventas/{venta['venta_id']}/productos/{producto_ejemplo['id']}"
        )
        assert response.status_code == 200


class TestAnularVenta:
    """Tests para anular ventas"""

    def test_anular_venta_completa(self, client, venta_completa, producto_ejemplo):
        """Debería anular venta y devolver stock"""
        stock_antes = client.get(f"/productos/{producto_ejemplo['id']}").json()["stock"]
        
        response = client.post(f"/ventas/{venta_completa['venta']['id']}/anular")
        
        assert response.status_code == 200
        data = response.json()
        assert "anulada" in data["mensaje"].lower()
        
        # Verificar que se devolvió el stock
        stock_despues = client.get(f"/productos/{producto_ejemplo['id']}").json()["stock"]
        assert stock_despues > stock_antes

    def test_no_anular_venta_ya_anulada(self, client, venta_completa):
        """NO debería poder anular dos veces"""
        # Anular primera vez
        client.post(f"/ventas/{venta_completa['venta']['id']}/anular")
        
        # Intentar anular segunda vez
        response = client.post(f"/ventas/{venta_completa['venta']['id']}/anular")
        assert response.status_code == 400