<template>
  <div>
    <div class="page-header">
      <div style="display:flex; align-items:center; justify-content:space-between">
        <div>
          <h1 class="page-title">📦 Productos</h1>
          <p class="page-subtitle">Gestión de inventario · {{ totalProductos }} productos</p>
        </div>
        <button class="btn btn-primary" @click="abrirCrear">
          + Nuevo Producto
        </button>
      </div>
    </div>

    <!-- Filtros -->
    <div class="card" style="margin-bottom: 20px; padding: 14px 16px;">
      <div style="display: grid; grid-template-columns: 1fr auto auto; gap: 12px; align-items: center;">
        <input
          v-model="buscar"
          class="input"
          placeholder="🔍  Buscar por nombre o código..."
          @input="filtrar"
        />
        <select v-model="filtroStock" class="input" style="width: 150px" @change="filtrar">
          <option value="">Todos</option>
          <option value="normal">🟢 Normal</option>
          <option value="bajo">🟡 Bajo mínimo</option>
          <option value="cero">🔴 Sin stock</option>
        </select>
        <select v-model="soloActivos" class="input" style="width: 130px" @change="cargar">
          <option :value="true">Solo activos</option>
          <option :value="false">Todos</option>
        </select>
      </div>
    </div>

    <!-- Tabla -->
    <div v-if="cargando" class="loading-center">
      <div class="spinner"></div>
    </div>

    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Código</th>
            <th>Nombre</th>
            <th>Stock</th>
            <th>Precio 1</th>
            <th>Precio 2</th>
            <th>Ubicación</th>
            <th>Sin Stock</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="productosFiltrados.length === 0">
            <td colspan="9" class="empty-state">
              <div class="empty-state-icon">📦</div>
              <div class="empty-state-text">No hay productos</div>
            </td>
          </tr>
          <tr v-for="p in productosFiltrados" :key="p.id">
            <td><span class="badge badge-gray">{{ p.codigo }}</span></td>
            <td style="font-weight: 500; max-width: 200px;">{{ p.nombre }}</td>
            <td>
              <div style="display:flex; align-items:center; gap:6px;">
                <span :class="stockBadgeClass(p)">{{ stockEmoji(p) }} {{ p.stock }}</span>
                <span style="font-size:10px; color:var(--color-muted)">/ {{ p.stock_minimo }}</span>
              </div>
            </td>
            <td style="font-weight: 600; color: var(--color-success)">Bs {{ fmt(p.precio1) }}</td>
            <td style="color: var(--color-muted)">{{ p.precio2 ? 'Bs ' + fmt(p.precio2) : '—' }}</td>
            <td>
              <span class="badge" :class="p.ubicacion === 'tienda' ? 'badge-blue' : 'badge-cyan'">
                {{ p.ubicacion === 'tienda' ? '🏪 Tienda' : '🏭 Bodega' }}
              </span>
            </td>
            <td>
              <span v-if="p.ventas_sin_stock > 0" class="badge badge-red">{{ p.ventas_sin_stock }}x</span>
              <span v-else style="color: var(--color-muted)">—</span>
            </td>
            <td>
              <span :class="p.activo ? 'badge badge-green' : 'badge badge-gray'">
                {{ p.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td>
              <div style="display:flex; gap:4px; flex-wrap:wrap;">
                <button class="btn btn-ghost btn-sm" title="Editar" @click="abrirEditar(p)">✏️</button>
                <button class="btn btn-ghost btn-sm" title="Ingresar stock" @click="abrirIngreso(p)" style="color:var(--color-success)">+📦</button>
                <button class="btn btn-ghost btn-sm" title="Ajustar stock" @click="abrirAjuste(p)" style="color:var(--color-warning)">🔧</button>
                <button class="btn btn-ghost btn-sm" title="Historial" @click="abrirHistorial(p)">📋</button>
                <button
                  v-if="p.activo"
                  class="btn btn-ghost btn-sm"
                  title="Descontinuar"
                  @click="descontinuar(p)"
                  style="color:var(--color-danger)"
                >🚫</button>
                <button
                  v-else
                  class="btn btn-ghost btn-sm"
                  title="Reactivar"
                  @click="reactivar(p)"
                  style="color:var(--color-success)"
                >✅</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Crear/Editar -->
    <div v-if="modalForm" class="modal-backdrop" @click.self="modalForm=null">
      <div class="modal">
        <div class="modal-header">
          <span class="modal-title">{{ modalForm.id ? '✏️ Editar Producto' : '+ Nuevo Producto' }}</span>
          <button class="btn btn-ghost btn-sm" @click="modalForm=null">✕</button>
        </div>
        <form @submit.prevent="guardarProducto">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Código *</label>
              <input v-model="modalForm.codigo" class="input" :disabled="!!modalForm.id" required />
            </div>
            <div class="form-group">
              <label class="form-label">Ubicación</label>
              <select v-model="modalForm.ubicacion" class="input">
                <option value="tienda">Tienda</option>
                <option value="bodega">Bodega</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Nombre *</label>
            <input v-model="modalForm.nombre" class="input" required />
          </div>
          <div class="form-group">
            <label class="form-label">Descripción</label>
            <input v-model="modalForm.descripcion" class="input" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Precio 1 * (Bs)</label>
              <input v-model.number="modalForm.precio1" type="number" step="0.01" min="0.01" class="input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Precio 2 (Bs)</label>
              <input v-model.number="modalForm.precio2" type="number" step="0.01" min="0" class="input" />
            </div>
            <div class="form-group">
              <label class="form-label">Precio 3 (Bs)</label>
              <input v-model.number="modalForm.precio3" type="number" step="0.01" min="0" class="input" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group" v-if="!modalForm.id">
              <label class="form-label">Stock Inicial</label>
              <input v-model.number="modalForm.stock_inicial" type="number" min="0" class="input" />
            </div>
            <div class="form-group">
              <label class="form-label">Stock Mínimo</label>
              <input v-model.number="modalForm.stock_minimo" type="number" min="0" class="input" />
            </div>
          </div>

          <div v-if="errorModal" class="alert alert-danger" style="margin-top:8px">{{ errorModal }}</div>

          <div style="display:flex; gap:8px; justify-content:flex-end; margin-top:16px">
            <button type="button" class="btn btn-secondary" @click="modalForm=null">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="guardando">
              <div v-if="guardando" class="spinner" style="width:14px;height:14px"></div>
              {{ modalForm.id ? 'Guardar Cambios' : 'Crear Producto' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Ingreso Stock -->
    <div v-if="modalIngreso" class="modal-backdrop" @click.self="modalIngreso=null">
      <div class="modal">
        <div class="modal-header">
          <span class="modal-title">+📦 Ingresar Stock</span>
          <button class="btn btn-ghost btn-sm" @click="modalIngreso=null">✕</button>
        </div>
        <p style="color:var(--color-muted); margin-bottom:16px; font-size:13px">
          {{ modalIngreso.nombre }} · Stock actual: <strong style="color:var(--color-accent)">{{ modalIngreso.stock }}</strong>
        </p>
        <div class="form-group">
          <label class="form-label">Cantidad a ingresar</label>
          <input v-model.number="ingresoForm.cantidad" type="number" min="1" class="input" autofocus />
        </div>
        <div class="form-group">
          <label class="form-label">Motivo</label>
          <select v-model="ingresoForm.motivo" class="input">
            <option value="compra">Compra</option>
            <option value="devolucion">Devolución</option>
            <option value="correccion">Corrección</option>
          </select>
        </div>
        <div v-if="errorModal" class="alert alert-danger">{{ errorModal }}</div>
        <div style="display:flex; gap:8px; justify-content:flex-end; margin-top:16px">
          <button class="btn btn-secondary" @click="modalIngreso=null">Cancelar</button>
          <button class="btn btn-success" @click="confirmarIngreso" :disabled="guardando">
            <div v-if="guardando" class="spinner" style="width:14px;height:14px"></div>
            Ingresar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Ajuste Stock -->
    <div v-if="modalAjuste" class="modal-backdrop" @click.self="modalAjuste=null">
      <div class="modal">
        <div class="modal-header">
          <span class="modal-title">🔧 Ajuste Manual de Stock</span>
          <button class="btn btn-ghost btn-sm" @click="modalAjuste=null">✕</button>
        </div>
        <p style="color:var(--color-muted); margin-bottom:16px; font-size:13px">
          {{ modalAjuste.nombre }} · Stock actual: <strong style="color:var(--color-warning)">{{ modalAjuste.stock }}</strong>
        </p>
        <div class="form-group">
          <label class="form-label">Nuevo stock real (inventario físico)</label>
          <input v-model.number="ajusteForm.nuevo_stock" type="number" min="0" class="input" autofocus />
        </div>
        <div v-if="errorModal" class="alert alert-danger">{{ errorModal }}</div>
        <div style="display:flex; gap:8px; justify-content:flex-end; margin-top:16px">
          <button class="btn btn-secondary" @click="modalAjuste=null">Cancelar</button>
          <button class="btn btn-primary" @click="confirmarAjuste" :disabled="guardando">
            <div v-if="guardando" class="spinner" style="width:14px;height:14px"></div>
            Ajustar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Historial -->
    <div v-if="modalHistorial" class="modal-backdrop" @click.self="modalHistorial=null">
      <div class="modal modal-lg">
        <div class="modal-header">
          <span class="modal-title">📋 Historial de Movimientos</span>
          <button class="btn btn-ghost btn-sm" @click="modalHistorial=null">✕</button>
        </div>
        <p style="color:var(--color-muted); margin-bottom:16px; font-size:13px">{{ modalHistorial.nombre }}</p>
        <div v-if="historialCargando" class="loading-center"><div class="spinner"></div></div>
        <div v-else class="table-wrapper" style="max-height: 400px; overflow-y: auto;">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Motivo</th>
                <th>Cantidad</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="historialData.length === 0">
                <td colspan="4" class="empty-state">Sin movimientos</td>
              </tr>
              <tr v-for="m in historialData" :key="m.id">
                <td style="white-space:nowrap; font-size:12px">{{ fmtFecha(m.fecha) }}</td>
                <td>
                  <span :class="tipoMovBadge(m.tipo)">{{ m.tipo }}</span>
                </td>
                <td style="font-size:12px; text-transform:capitalize">{{ m.motivo }}</td>
                <td style="font-weight:700" :style="m.tipo === 'salida' ? 'color:var(--color-danger)' : 'color:var(--color-success)'">
                  {{ m.tipo === 'salida' ? '-' : '+' }}{{ m.cantidad }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { productos as productosApi } from '@/api/productos'

const lista = ref([])
const cargando = ref(true)
const buscar = ref('')
const filtroStock = ref('')
const soloActivos = ref(true)
const totalProductos = ref(0)

const modalForm = ref(null)
const modalIngreso = ref(null)
const modalAjuste = ref(null)
const modalHistorial = ref(null)
const historialData = ref([])
const historialCargando = ref(false)
const guardando = ref(false)
const errorModal = ref('')
const ingresoForm = ref({ cantidad: 1, motivo: 'compra' })
const ajusteForm = ref({ nuevo_stock: 0 })

const productosFiltrados = computed(() => {
  let result = lista.value
  if (buscar.value) {
    const q = buscar.value.toLowerCase()
    result = result.filter(p =>
      p.nombre.toLowerCase().includes(q) || p.codigo.toLowerCase().includes(q)
    )
  }
  if (filtroStock.value === 'normal') {
    result = result.filter(p => p.stock > p.stock_minimo)
  } else if (filtroStock.value === 'bajo') {
    result = result.filter(p => p.stock > 0 && p.stock <= p.stock_minimo)
  } else if (filtroStock.value === 'cero') {
    result = result.filter(p => p.stock === 0)
  }
  return result
})

function stockEmoji(p) {
  if (p.stock === 0) return '🔴'
  if (p.stock <= p.stock_minimo) return '🟡'
  return '🟢'
}
function stockBadgeClass(p) {
  if (p.stock === 0) return 'badge badge-red'
  if (p.stock <= p.stock_minimo) return 'badge badge-yellow'
  return 'badge badge-green'
}
function tipoMovBadge(tipo) {
  if (tipo === 'ingreso') return 'badge badge-green'
  if (tipo === 'salida') return 'badge badge-red'
  return 'badge badge-yellow'
}
function fmt(n) {
  return Number(n || 0).toFixed(2)
}
function fmtFecha(f) {
  return new Date(f).toLocaleString('es-BO', { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function cargar() {
  cargando.value = true
  try {
    const res = await productosApi.listar({ solo_activos: soloActivos.value, limit: 500 })
    lista.value = res.data
    totalProductos.value = res.data.length
  } catch (e) {
    console.error(e)
  } finally {
    cargando.value = false
  }
}

function filtrar() { /* reactivo por computed */ }

function abrirCrear() {
  errorModal.value = ''
  modalForm.value = {
    codigo: '', nombre: '', descripcion: '',
    precio1: '', precio2: null, precio3: null, precio4: null,
    stock_inicial: 0, stock_minimo: 5, ubicacion: 'tienda'
  }
}
function abrirEditar(p) {
  errorModal.value = ''
  modalForm.value = { ...p }
}
function abrirIngreso(p) {
  errorModal.value = ''
  ingresoForm.value = { cantidad: 1, motivo: 'compra' }
  modalIngreso.value = p
}
function abrirAjuste(p) {
  errorModal.value = ''
  ajusteForm.value = { nuevo_stock: p.stock }
  modalAjuste.value = p
}
async function abrirHistorial(p) {
  modalHistorial.value = p
  historialCargando.value = true
  historialData.value = []
  try {
    const res = await productosApi.historial(p.id)
    historialData.value = res.data?.movimientos || res.data || []
  } catch (e) {
    historialData.value = []
  } finally {
    historialCargando.value = false
  }
}

async function guardarProducto() {
  guardando.value = true
  errorModal.value = ''
  try {
    if (modalForm.value.id) {
      const { id, codigo, stock, activo, fecha_creacion, fecha_edicion, ventas_sin_stock, ...datos } = modalForm.value
      await productosApi.actualizar(id, datos)
    } else {
      await productosApi.crear(modalForm.value)
    }
    modalForm.value = null
    await cargar()
  } catch (e) {
    errorModal.value = e.message
  } finally {
    guardando.value = false
  }
}

async function confirmarIngreso() {
  if (!ingresoForm.value.cantidad || ingresoForm.value.cantidad < 1) return
  guardando.value = true
  errorModal.value = ''
  try {
    await productosApi.ingresarStock(modalIngreso.value.id, ingresoForm.value.cantidad, ingresoForm.value.motivo)
    modalIngreso.value = null
    await cargar()
  } catch (e) {
    errorModal.value = e.message
  } finally {
    guardando.value = false
  }
}

async function confirmarAjuste() {
  guardando.value = true
  errorModal.value = ''
  try {
    await productosApi.ajustarStock(modalAjuste.value.id, ajusteForm.value.nuevo_stock)
    modalAjuste.value = null
    await cargar()
  } catch (e) {
    errorModal.value = e.message
  } finally {
    guardando.value = false
  }
}

async function descontinuar(p) {
  if (!confirm(`¿Descontinuar "${p.nombre}"?`)) return
  try {
    await productosApi.descontinuar(p.id)
    await cargar()
  } catch (e) {
    alert(e.message)
  }
}

async function reactivar(p) {
  try {
    await productosApi.reactivar(p.id)
    await cargar()
  } catch (e) {
    alert(e.message)
  }
}

onMounted(cargar)
</script>
