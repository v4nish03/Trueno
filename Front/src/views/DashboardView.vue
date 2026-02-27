<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <p class="page-subtitle">Resumen del negocio — {{ fechaHoy }}</p>
    </div>

    <!-- KPIs -->
    <div v-if="cargando" class="loading-center">
      <div class="spinner"></div>
      <span>Cargando datos...</span>
    </div>

    <template v-else>
      <div class="kpi-grid">
        <div class="kpi-card accent">
          <div class="kpi-label">Ventas de hoy</div>
          <div class="kpi-value" style="color: var(--color-accent)">
            Bs {{ fmt(datos?.hoy?.total ?? 0) }}
          </div>
          <div class="kpi-sub">{{ datos?.hoy?.ventas ?? 0 }} transacciones</div>
        </div>

        <div class="kpi-card cyan">
          <div class="kpi-label">Últimos 30 días</div>
          <div class="kpi-value" style="color: var(--color-accent-2)">
            Bs {{ fmt(datos?.ultimo_mes?.total ?? 0) }}
          </div>
          <div class="kpi-sub">
            {{ datos?.ultimo_mes?.ventas ?? 0 }} ventas · Bs {{ fmt(datos?.ultimo_mes?.promedio_diario ?? 0) }}/día
          </div>
        </div>

        <div class="kpi-card warning">
          <div class="kpi-label">Stock Bajo</div>
          <div class="kpi-value" style="color: var(--color-warning)">
            {{ datos?.alertas?.productos_stock_bajo ?? 0 }}
          </div>
          <div class="kpi-sub">productos bajo el mínimo</div>
        </div>

        <div class="kpi-card danger">
          <div class="kpi-label">Sin Stock Vendidos</div>
          <div class="kpi-value" style="color: var(--color-danger)">
            {{ datos?.alertas?.productos_ventas_sin_stock ?? 0 }}
          </div>
          <div class="kpi-sub">productos con deuda de stock</div>
        </div>

        <div class="kpi-card success">
          <div class="kpi-label">Última semana</div>
          <div class="kpi-value" style="color: var(--color-success)">
            Bs {{ fmt(datos?.ultima_semana?.total ?? 0) }}
          </div>
          <div class="kpi-sub">{{ datos?.ultima_semana?.ventas ?? 0 }} ventas en 7 días</div>
        </div>
      </div>

      <!-- Alertas activas -->
      <div v-if="alertasStore.totalStockBajo > 0 || alertasStore.totalSinStock > 0" style="margin: 24px 0 0">
        <div class="section-header">
          <span class="section-title">🚨 Alertas Activas</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <!-- Stock bajo -->
          <div v-if="alertasStore.stockBajo.length" class="card">
            <div class="section-header">
              <span class="section-title" style="font-size:13px; color: var(--color-warning)">
                ⚠️ Stock Bajo ({{ alertasStore.totalStockBajo }})
              </span>
              <router-link to="/productos" class="btn btn-ghost btn-sm">Ver todos →</router-link>
            </div>
            <div v-for="p in alertasStore.stockBajo.slice(0,5)" :key="p.id" class="alert-row">
              <span class="alert-row-name">{{ p.nombre }}</span>
              <span class="badge badge-yellow">{{ p.stock }} / {{ p.stock_minimo }}</span>
            </div>
          </div>
          <!-- Sin stock -->
          <div v-if="alertasStore.ventasSinStock.length" class="card">
            <div class="section-header">
              <span class="section-title" style="font-size:13px; color: var(--color-danger)">
                🔴 Vendidos sin Stock ({{ alertasStore.totalSinStock }})
              </span>
              <router-link to="/productos" class="btn btn-ghost btn-sm">Ver todos →</router-link>
            </div>
            <div v-for="p in alertasStore.ventasSinStock.slice(0,5)" :key="p.id" class="alert-row">
              <span class="alert-row-name">{{ p.nombre }}</span>
              <span class="badge badge-red">{{ p.ventas_sin_stock }} veces</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Métodos de pago + Top ventas -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 24px;">
        <!-- Métodos de pago -->
        <div class="card">
          <div class="section-title" style="margin-bottom: 16px">💳 Métodos de Pago (histórico)</div>
          <div v-if="metodoPago.length === 0" class="empty-state" style="padding: 24px">
            <div class="empty-state-text">Sin datos</div>
          </div>
          <div v-for="m in metodoPago" :key="m.metodo_pago" class="metodo-row">
            <div class="metodo-icon">{{ m.metodo_pago === 'efectivo' ? '💵' : '📱' }}</div>
            <div style="flex:1">
              <div style="font-weight: 600; text-transform: capitalize; font-size:13px">{{ m.metodo_pago }}</div>
              <div style="font-size:11px; color: var(--color-muted)">{{ m.cantidad_ventas }} ventas</div>
            </div>
            <div style="font-weight: 700; color: var(--color-accent)">Bs {{ fmt(m.total) }}</div>
          </div>
        </div>

        <!-- Top productos -->
        <div class="card">
          <div class="section-title" style="margin-bottom: 16px">🏆 Top Productos (últimos 30 días)</div>
          <div v-if="topProductos.length === 0" class="empty-state" style="padding: 24px">
            <div class="empty-state-text">Sin datos de ventas</div>
          </div>
          <div v-for="(p, i) in topProductos.slice(0, 5)" :key="p.producto_id" class="top-row">
            <span class="top-rank">{{ i + 1 }}</span>
            <div style="flex:1; min-width:0">
              <div style="font-weight:600; font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis">
                {{ p.nombre }}
              </div>
              <div style="font-size:11px; color: var(--color-muted)">{{ p.cantidad_vendida }} unidades</div>
            </div>
            <div style="font-weight:700; font-size:12px; color: var(--color-success)">Bs {{ fmt(p.ingreso_total) }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { reportes as reportesApi } from '@/api/reportes'
import { useAlertasStore } from '@/stores/alertas'

const alertasStore = useAlertasStore()
const cargando = ref(true)
const datos = ref(null)
const metodoPago = ref([])
const topProductos = ref([])

const fechaHoy = new Date().toLocaleDateString('es-BO', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
})

function fmt(n) {
  return Number(n || 0).toLocaleString('es-BO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function cargar() {
  cargando.value = true
  try {
    const hoy = new Date()
    const hace30 = new Date(hoy)
    hace30.setDate(hace30.getDate() - 30)
    const fmtDate = (d) => d.toISOString().split('T')[0]

    const [r1, r2, r3] = await Promise.all([
      reportesApi.dashboard(),
      reportesApi.porMetodoPago(),
      reportesApi.productosMasVendidos(fmtDate(hace30), fmtDate(hoy)),
    ])
    datos.value = r1.data
    metodoPago.value = r2.data || []
    topProductos.value = r3.data?.productos || []
  } catch (e) {
    console.error('Error cargando dashboard:', e)
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.alert-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 12px;
}
.alert-row:last-child { border-bottom: none; }
.alert-row-name {
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
  font-weight: 500;
}

.metodo-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border);
}
.metodo-row:last-child { border-bottom: none; }
.metodo-icon { font-size: 20px; }

.top-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
}
.top-row:last-child { border-bottom: none; }
.top-rank {
  width: 22px;
  height: 22px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-accent);
  flex-shrink: 0;
}
</style>
