# ========== test_alertas.py ==========
import pytest


class TestAlertas:
    """Tests para sistema de alertas"""

    def test_alertas_stock_bajo(self, client, producto_ejemplo):
        """Debería detectar productos con stock bajo"""
        # Ajustar stock por debajo del mínimo
        client.post(f"/productos/{producto_ejemplo['id']}/ajustar-stock?nuevo_stock=5")
        
        response = client.get("/alertas/stock-bajo")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_alertas_ventas_sin_stock(self, client, producto_sin_stock):
        """Debería detectar ventas sin stock"""
        # Hacer una venta sin stock
        venta = client.post("/ventas/abrir").json()
        client.post(
            f"/ventas/{venta['venta_id']}/productos",
            json={
                "producto_id": producto_sin_stock["id"],
                "cantidad": 10,
                "precio_unitario": 50.0
            }
        )
        client.post(f"/ventas/{venta['venta_id']}/cerrar", json={"metodo_pago": "efectivo"})
        
        response = client.get("/alertas/ventas-sin-stock")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_alerta_detallada_incluye_recibo_y_fecha(self, client, producto_sin_stock, monkeypatch):
        """La alerta detallada debe incluir venta, recibo y fecha"""
        from services import alertas_service

        capturado = {"texto": None}

        def fake_send(texto):
            capturado["texto"] = texto
            return True

        monkeypatch.setattr(alertas_service, "enviar_mensaje", fake_send)

        venta = client.post("/ventas/abrir").json()
        client.post(
            f"/ventas/{venta['venta_id']}/productos",
            json={
                "producto_id": producto_sin_stock["id"],
                "cantidad": 2,
                "precio_unitario": 50.0
            }
        )

        response = client.post(
            f"/ventas/{venta['venta_id']}/cerrar",
            json={"metodo_pago": "efectivo"}
        )

        assert response.status_code == 200
        assert capturado["texto"] is not None
        assert "Venta N°" in capturado["texto"]
        assert "Recibo N°" in capturado["texto"]
        assert "Fecha venta" in capturado["texto"]
