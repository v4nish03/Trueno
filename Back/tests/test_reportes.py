# ========== test_reportes.py ==========
from datetime import date


class TestReportes:
    """Tests para reportes"""

    def test_dashboard(self, client, venta_completa):
        """Debería obtener el dashboard con resumen"""
        response = client.get("/reportes/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "hoy" in data
        assert "ultima_semana" in data
        assert "ultimo_mes" in data
        assert "alertas" in data

    def test_reporte_ventas_diarias(self, client, venta_completa):
        """Debería generar reporte de ventas del día"""
        hoy = date.today()
        response = client.get(f"/reportes/ventas-diarias?fecha={hoy}")
        assert response.status_code == 200
        data = response.json()
        assert "cantidad_ventas" in data
        assert "total_vendido" in data

    def test_reporte_mensual(self, client, venta_completa):
        """Debería generar reporte mensual"""
        hoy = date.today()
        response = client.get(f"/reportes/mensual?year={hoy.year}&month={hoy.month}")
        assert response.status_code == 200
        data = response.json()
        assert "cantidad_ventas" in data
        assert "total_vendido" in data

    def test_reporte_productos_mas_vendidos(self, client, venta_completa):
        """Debería mostrar productos más vendidos"""
        hoy = date.today()
        response = client.get(
            f"/reportes/productos-mas-vendidos?fecha_inicio={hoy}&fecha_fin={hoy}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "productos" in data

    def test_reporte_por_metodo_pago(self, client, venta_completa):
        """Debería agrupar ventas por método de pago"""
        response = client.get("/reportes/por-metodo-pago")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_reporte_ventas_sin_stock(self, client, producto_sin_stock):
        """Debería reportar ventas sin stock"""
        # Crear venta sin stock
        venta = client.post("/ventas/abrir").json()
        client.post(
            f"/ventas/{venta['venta_id']}/productos",
            json={
                "producto_id": producto_sin_stock["id"],
                "cantidad": 5,
                "precio_unitario": 50.0
            }
        )
        client.post(f"/ventas/{venta['venta_id']}/cerrar", json={"metodo_pago": "efectivo"})
        
        response = client.get("/reportes/ventas-sin-stock")
        assert response.status_code == 200
        data = response.json()
        assert data["total_productos_afectados"] >= 1
