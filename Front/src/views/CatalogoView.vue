<template>
  <div>
    <div class="page-header" style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px; flex-wrap:wrap;">
      <div>
        <h1 class="page-title">🖼️ Catálogo de Productos</h1>
        <p class="page-subtitle">Genera catálogo general o por categorías seleccionadas.</p>
      </div>
      <button class="btn btn-primary" @click="generarPdf" :disabled="generandoPdf">
        {{ generandoPdf ? 'Generando...' : '📄 Generar PDF' }}
      </button>
    </div>

    <div class="card filtros-catalogo no-print">
      <div class="form-group" style="min-width:260px; margin:0;">
        <label class="form-label">Buscar categoría</label>
        <input v-model="busquedaCategoria" class="input" placeholder="Ej: Lubricantes" />
      </div>

      <div class="categoria-box">
        <div class="categoria-header">
          <strong>Categorías</strong>
          <div style="display:flex; gap:8px;">
            <button class="btn btn-ghost btn-sm" @click="seleccionarTodas">Todas</button>
            <button class="btn btn-ghost btn-sm" @click="limpiarSeleccion">General</button>
          </div>
        </div>

        <label class="categoria-item" v-for="cat in categoriasFiltradas" :key="cat">
          <input type="checkbox" :value="cat" v-model="categoriasSeleccionadas" @change="cargarProductos" />
          <span>{{ cat }}</span>
        </label>

        <div v-if="categoriasFiltradas.length === 0" class="empty-cat">Sin categorías para mostrar.</div>
      </div>

      <label style="display:flex; align-items:center; gap:8px; font-size:13px; color:var(--color-muted); margin:0;">
        <input type="checkbox" v-model="soloConImagen" @change="cargarProductos" />
        Solo productos con imagen
      </label>
    </div>

    <div class="print-header">
      <img v-if="catalogoPdfConfig.branding.logoUrl" :src="catalogoPdfConfig.branding.logoUrl" class="logo-print" alt="Logo" />
      <div>
        <h2>{{ catalogoPdfConfig.tienda.nombre }}</h2>
        <p>{{ catalogoPdfConfig.tienda.sucursal }} · {{ catalogoPdfConfig.tienda.telefono }}</p>
        <p>{{ catalogoPdfConfig.tienda.direccion }}</p>
        <p>{{ catalogoPdfConfig.tienda.mensaje }}</p>
      </div>
    </div>

    <div v-if="cargando" class="loading-center"><div class="spinner"></div></div>

    <div v-else>
      <div v-if="productos.length === 0" class="card empty-state" style="padding:26px;">
        <div class="empty-state-icon">🗂️</div>
        <div class="empty-state-text">No hay productos para este catálogo.</div>
      </div>

      <section v-for="grupo in productosAgrupados" :key="grupo.categoria" class="categoria-seccion">
        <div class="categoria-titulo">{{ grupo.categoria }}</div>

        <div class="catalogo-grid">
          <article class="catalogo-item card" v-for="p in grupo.items" :key="p.id">
            <img v-if="p.imagen_url" :src="p.imagen_url" :alt="p.nombre" class="catalogo-imagen" />
            <div v-else class="sin-imagen">Sin imagen</div>

            <div class="catalogo-info">
              <h3>{{ p.nombre }}</h3>
              <p class="codigo">Cod: {{ p.codigo }}</p>
              <p class="precio">{{ catalogoPdfConfig.pdf.moneda }} {{ fmt(p.precio1) }}</p>
              <p v-if="p.descripcion" class="desc">{{ p.descripcion }}</p>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { productos as productosApi } from '@/api/productos'
import { catalogoPdfConfig } from '@/config/catalogoPdfConfig'

const categorias = ref([])
const categoriasSeleccionadas = ref([])
const busquedaCategoria = ref('')
const soloConImagen = ref(false)
const productos = ref([])
const cargando = ref(true)
const generandoPdf = ref(false)

const categoriasFiltradas = computed(() => {
  const q = busquedaCategoria.value.trim().toLowerCase()
  if (!q) return categorias.value
  return categorias.value.filter((cat) => cat.toLowerCase().includes(q))
})

const productosAgrupados = computed(() => {
  const grupos = new Map()
  for (const p of productos.value) {
    const cat = p.categoria || 'General'
    if (!grupos.has(cat)) grupos.set(cat, [])
    grupos.get(cat).push(p)
  }
  return Array.from(grupos.entries())
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([categoria, items]) => ({ categoria, items }))
})

function fmt(n) {
  return Number(n || 0).toFixed(2)
}

async function cargarCategorias() {
  const res = await productosApi.categorias({ solo_activos: true })
  categorias.value = res.data || []
}

async function cargarProductos() {
  cargando.value = true
  try {
    const paramsBase = {
      solo_activos: true,
      limit: 500,
      solo_con_imagen: soloConImagen.value,
    }

    if (categoriasSeleccionadas.value.length === 0) {
      const res = await productosApi.listar(paramsBase)
      productos.value = res.data || []
      return
    }

    const respuestas = await Promise.all(
      categoriasSeleccionadas.value.map((categoria) =>
        productosApi.listar({ ...paramsBase, categoria })
      )
    )

    const porId = new Map()
    for (const r of respuestas) {
      for (const item of r.data || []) {
        porId.set(item.id, item)
      }
    }
    productos.value = Array.from(porId.values())
  } catch (error) {
    console.error('Error cargando catálogo', error)
    productos.value = []
  } finally {
    cargando.value = false
  }
}

async function seleccionarTodas() {
  categoriasSeleccionadas.value = [...categoriasFiltradas.value]
  await cargarProductos()
}

async function limpiarSeleccion() {
  categoriasSeleccionadas.value = []
  await cargarProductos()
}

async function generarPdf() {
  generandoPdf.value = true
  try {
    const params = {
      solo_activos: true,
      solo_con_imagen: soloConImagen.value,
    }
    if (categoriasSeleccionadas.value.length > 0) {
      params.categorias = categoriasSeleccionadas.value
    }

    const res = await productosApi.descargarCatalogoPdf(params)
    const blob = new Blob([res.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'catalogo_productos.pdf'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('No se pudo generar el PDF', error)
    alert('No se pudo generar el PDF del catálogo')
  } finally {
    generandoPdf.value = false
  }
}

onMounted(async () => {
  await cargarCategorias()
  await cargarProductos()
})
</script>

<style scoped>
.filtros-catalogo {
  margin-bottom: 16px;
  display: grid;
  gap: 12px;
}
.categoria-box {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 10px;
  max-height: 190px;
  overflow: auto;
}
.categoria-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.categoria-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  padding: 4px 0;
}
.empty-cat { color: var(--color-muted); font-size: 12px; }

.print-header {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid var(--color-border);
  background: var(--color-surface-2);
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 12px;
}
.print-header h2 { margin: 0; }
.print-header p { margin: 2px 0; color: var(--color-muted); font-size: 12px; }
.logo-print {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid var(--color-border);
}

.categoria-seccion { margin-bottom: 16px; }
.categoria-titulo {
  font-weight: 700;
  margin-bottom: 8px;
  border-left: 4px solid var(--color-accent);
  padding-left: 8px;
}
.catalogo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 14px;
}
.catalogo-item { padding: 10px; }
.catalogo-imagen {
  width: 100%;
  height: 150px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid var(--color-border);
  background: #0f172a;
}
.sin-imagen {
  width: 100%;
  height: 150px;
  border-radius: 8px;
  border: 1px dashed var(--color-border);
  display: grid;
  place-items: center;
  color: var(--color-muted);
  font-size: 12px;
}
.catalogo-info { padding: 8px 2px 2px; }
h3 { margin: 0; font-size: 14px; }
.codigo { font-size: 11px; color: var(--color-muted); margin: 4px 0; }
.precio { color: var(--color-success); font-weight: 700; margin: 0 0 4px; }
.desc { font-size: 12px; color: var(--color-muted); margin: 0; }

@media print {
  .no-print,
  .page-header {
    display: none !important;
  }
  .print-header {
    break-inside: avoid;
    border: none;
    border-bottom: 2px solid #000;
    border-radius: 0;
    padding: 0 0 8px;
    margin-bottom: 14px;
    background: #fff;
  }
  .card {
    border: 1px solid #ccc !important;
    box-shadow: none !important;
    background: #fff !important;
  }
}
</style>
