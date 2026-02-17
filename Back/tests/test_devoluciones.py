import pytest


class TestDevoluciones:
    """Tests para devoluciones de productos"""

    def test_devolver_producto_parcial(self, client, venta_completa, producto_ejemplo):
        """Debería devolver parte de un producto"""
        stock_antes = client.get(f"/productos/{producto_ejemplo['id']}").json()["stock"]
        total_antes = venta_completa["venta"]["total"]
        
        response = client.post(
            f"/devoluciones/{venta_completa['venta']['id']}/productos",
            json={
                "producto_id": producto_ejemplo["id"],
                "cantidad": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["cantidad_devuelta"] == 2
        assert data["monto_devuelto"] > 0
        assert data["nuevo_total_venta"] < total_antes
        
        # Verificar que aumentó el stock
        stock_despues = client.get(f"/productos/{producto_ejemplo['id']}").json()["stock"]
        assert stock_despues == stock_antes + 2

    def test_devolver_producto_completo(self, client, venta_completa, producto_ejemplo):
        """Debería devolver todo el producto"""
        # En venta_abierta se agregan 5 unidades
        response = client.post(
            f"/devoluciones/{venta_completa['venta']['id']}/productos",
            json={
                "producto_id": producto_ejemplo["id"],
                "cantidad": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["cantidad_devuelta"] == 5
        assert data["nuevo_total_venta"] == 0

    def test_no_devolver_mas_de_lo_vendido(self, client, venta_completa, producto_ejemplo):
        """NO debería permitir devolver más de lo vendido"""
        response = client.post(
            f"/devoluciones/{venta_completa['venta']['id']}/productos",
            json={
                "producto_id": producto_ejemplo["id"],
                "cantidad": 100  # Más de lo vendido
            }
        )
        
        assert response.status_code == 400
        assert "inválida" in response.json()["detail"].lower()

    def test_no_devolver_de_venta_anulada(self, client, venta_completa, producto_ejemplo):
        """NO debería permitir devolver de venta anulada"""
        # Anular venta
        client.post(f"/ventas/{venta_completa['venta']['id']}/anular")
        
        # Intentar devolver
        response = client.post(
            f"/devoluciones/{venta_completa['venta']['id']}/productos",
            json={
                "producto_id": producto_ejemplo["id"],
                "cantidad": 1
            }
        )
        
        assert response.status_code == 400
        assert "anulada" in response.json()["detail"].lower()

    def test_devolver_producto_inexistente_en_venta(self, client, venta_completa):
        """NO debería devolver producto que no está en la venta"""
        response = client.post(
            f"/devoluciones/{venta_completa['venta']['id']}/productos",
            json={
                "producto_id": 99999,
                "cantidad": 1
            }
        )
        
        assert response.status_code == 400