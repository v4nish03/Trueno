<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">📊 Movimientos de Inventario</h1>
      <p class="page-subtitle">Ingresos, salidas y ajustes de stock</p>
    </div>

    <!-- Filtros -->
    <div class="card" style="margin-bottom: 20px; padding: 14px 16px;">
      <div style="display: grid; grid-template-columns: 1fr auto auto auto; gap: 12px; align-items: center;">
        <input v-model="filtroBuscar" class="input" placeholder="🔍  Buscar producto..." @input="cargar" />
        <select v-model="filtroTipo" class="input" style="width: 140px" @change="cargar">
          <option value="">Todos los tipos</option>
          <option value="ingreso">📥 Ingreso</option>
          <option value="salida">📤 Salida</option>
          <option value="ajuste">🔧 Ajuste</option>
        </select>
        <input v-model="filtroDesde" type="date" class="input" style="width: 140px" @change="cargar" />
        <input v-model="filtroHasta" type="date" class="input" style="width: 140px" @change="cargar" />
      </div>
    </div>

    <div v-if="cargando" class="loading-center"><div class="spinner"></div></div>

    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Fecha</th>
            <th>Producto</th>
            <th>Tipo</th>
            <th>Motivo</th>
            <th>Cantidad</th>
            <th>Ref.</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="movimientos.length === 0">
            <td colspan="7" class="empty-state">
              <div class="empty-state-icon">📊</div>
              <div class="empty-state-text">Sin movimientos para los filtros aplicados</div>
            </td>
          </tr>
          <tr v-for="m in movimientos" :key="m.id">
            <td style="color:var(--color-muted); font-size:11px">{{ m.id }}</td>
            <td style="font-size:12px; white-space:nowrap">{{ fmtFecha(m.fecha) }}</td>
            <td>
              <div style="font-weight:500; font-size:12px">{{ m.nombre_producto || m.producto_id }}</div>
              <div style="font-size:11px; color:var(--color-muted)">{{ m.codigo_producto || '' }}</div>
            </td>
            <td>
              <span :class="tipoBadge(m.tipo)">{{ m.tipo }}</span>
            </td>
            <td>
              <span class="badge badge-gray" style="text-transform:capitalize">{{ m.motivo }}</span>
            </td>
            <td>
              <span
                style="font-weight:800; font-size:14px"
                :style="m.tipo === 'salida' ? 'color:var(--color-danger)' : 'color:var(--color-success)'"
              >
                {{ m.tipo === 'salida' ? '−' : '+' }}{{ m.cantidad }}
              </span>
            </td>
            <td style="color:var(--color-muted); font-size:11px">
              {{ m.referencia_id ? '#' + m.referencia_id : '—' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Resumen -->
    <div v-if="!cargando && movimientos.length > 0" style="margin-top:16px; display:flex; gap:12px;">
      <div class="kpi-card success" style="flex:1; padding:12px 16px">
        <div class="kpi-label">Total Ingresos</div>
        <div style="font-size:20px; font-weight:800; color:var(--color-success)">+{{ sumaIngreso }}</div>
        <div class="kpi-sub">unidades ingresadas</div>
      </div>
      <div class="kpi-card danger" style="flex:1; padding:12px 16px">
        <div class="kpi-label">Total Salidas</div>
        <div style="font-size:20px; font-weight:800; color:var(--color-danger)">−{{ sumaSalida }}</div>
        <div class="kpi-sub">unidades salidas</div>
      </div>
      <div class="kpi-card warning" style="flex:1; padding:12px 16px">
        <div class="kpi-label">Ajustes</div>
        <div style="font-size:20px; font-weight:800; color:var(--color-warning)">{{ sumaAjuste }}</div>
        <div class="kpi-sub">correcciones</div>
      </div>
      <div class="kpi-card accent" style="flex:1; padding:12px 16px">
        <div class="kpi-label">Total movimientos</div>
        <div style="font-size:20px; font-weight:800; color:var(--color-accent)">{{ movimientos.length }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { productos as productosApi } from '@/api/productos'

const movimientos = ref([])
const cargando = ref(true)
const filtroBuscar = ref('')
const filtroTipo = ref('')
const filtroDesde = ref('')
const filtroHasta = ref('')

// Cargamos productos y sus historial de movimientos
const todosLosProductos = ref([])

const sumaIngreso = computed(() =>
  movimientos.value.filter(m => m.tipo === 'ingreso').reduce((s, m) => s + m.cantidad, 0)
)
const sumaSalida = computed(() =>
  movimientos.value.filter(m => m.tipo === 'salida').reduce((s, m) => s + m.cantidad, 0)
)
const sumaAjuste = computed(() => movimientos.value.filter(m => m.tipo === 'ajuste').length)

function tipoBadge(tipo) {
  if (tipo === 'ingreso') return 'badge badge-green'
  if (tipo === 'salida') return 'badge badge-red'
  return 'badge badge-yellow'
}

function fmtFecha(f) {
  return new Date(f).toLocaleString('es-BO', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

async function cargar() {
  cargando.value = true
  try {
    // Obtenemos todos los productos para cruzar nombres
    const res = await productosApi.listar({ limit: 500, solo_activos: false })
    todosLosProductos.value = res.data

    // Para cada producto, obtenemos su historial
    const todos = []
    await Promise.all(
      res.data.map(async (p) => {
        try {
          const h = await productosApi.historial(p.id)
          const movs = h.data?.movimientos || h.data || []
          movs.forEach(m => {
            todos.push({ ...m, nombre_producto: p.nombre, codigo_producto: p.codigo })
          })
        } catch (_) {}
      })
    )

    // Ordenar por fecha desc
    todos.sort((a, b) => new Date(b.fecha) - new Date(a.fecha))

    // Aplicar filtros
    let resultado = todos

    if (filtroTipo.value) {
      resultado = resultado.filter(m => m.tipo === filtroTipo.value)
    }

    if (filtroBuscar.value) {
      const q = filtroBuscar.value.toLowerCase()
      resultado = resultado.filter(m =>
        m.nombre_producto?.toLowerCase().includes(q) ||
        m.codigo_producto?.toLowerCase().includes(q)
      )
    }

    if (filtroDesde.value) {
      const desde = new Date(filtroDesde.value)
      resultado = resultado.filter(m => new Date(m.fecha) >= desde)
    }

    if (filtroHasta.value) {
      const hasta = new Date(filtroHasta.value + 'T23:59:59')
      resultado = resultado.filter(m => new Date(m.fecha) <= hasta)
    }

    movimientos.value = resultado
  } catch (e) {
    console.error(e)
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>
