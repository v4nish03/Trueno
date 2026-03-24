<template>
  <div>
    <div class="page-header" style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px; flex-wrap:wrap;">
      <div>
        <h1 class="page-title">🖼️ Catálogo de Productos</h1>
        <p class="page-subtitle">Genera catálogo general o por categoría sin afectar ventas/inventario.</p>
      </div>
      <button class="btn btn-secondary" @click="imprimirCatalogo">🖨️ Imprimir / Guardar PDF</button>
    </div>

    <div class="card" style="margin-bottom:16px; display:flex; gap:12px; align-items:end; flex-wrap:wrap;">
      <div class="form-group" style="min-width:200px; margin:0;">
        <label class="form-label">Categoría</label>
        <select v-model="categoriaSeleccionada" class="input" @change="cargarProductos">
          <option value="">General (todas)</option>
          <option v-for="cat in categorias" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </div>
      <label style="display:flex; align-items:center; gap:8px; font-size:13px; color:var(--color-muted); margin-bottom:10px;">
        <input type="checkbox" v-model="soloConImagen" @change="cargarProductos" />
        Solo productos con imagen
      </label>
    </div>

    <div v-if="cargando" class="loading-center"><div class="spinner"></div></div>

    <div v-else>
      <div v-if="productos.length === 0" class="card empty-state" style="padding:26px;">
        <div class="empty-state-icon">🗂️</div>
        <div class="empty-state-text">No hay productos para este catálogo.</div>
      </div>

      <div v-else class="catalogo-grid" id="zona-catalogo">
        <article class="catalogo-item card" v-for="p in productos" :key="p.id">
          <img
            v-if="p.imagen_url"
            :src="p.imagen_url"
            :alt="p.nombre"
            class="catalogo-imagen"
          />
          <div v-else class="sin-imagen">Sin imagen</div>
          <div class="catalogo-info">
            <div class="catalogo-categoria">{{ p.categoria || 'General' }}</div>
            <h3>{{ p.nombre }}</h3>
            <p class="codigo">Cod: {{ p.codigo }}</p>
            <p class="precio">Bs {{ fmt(p.precio1) }}</p>
            <p v-if="p.descripcion" class="desc">{{ p.descripcion }}</p>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { productos as productosApi } from '@/api/productos'

const categorias = ref([])
const categoriaSeleccionada = ref('')
const soloConImagen = ref(false)
const productos = ref([])
const cargando = ref(true)

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
    const params = {
      solo_activos: true,
      limit: 500,
      solo_con_imagen: soloConImagen.value,
    }
    if (categoriaSeleccionada.value) {
      params.categoria = categoriaSeleccionada.value
    }
    const res = await productosApi.listar(params)
    productos.value = res.data || []
  } catch (error) {
    console.error('Error cargando catálogo', error)
    productos.value = []
  } finally {
    cargando.value = false
  }
}

function imprimirCatalogo() {
  window.print()
}

onMounted(async () => {
  await cargarCategorias()
  await cargarProductos()
})
</script>

<style scoped>
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
.catalogo-categoria {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 10px;
  border: 1px solid var(--color-border);
  color: var(--color-muted);
  margin-bottom: 6px;
}
h3 { margin: 0; font-size: 14px; }
.codigo { font-size: 11px; color: var(--color-muted); margin: 4px 0; }
.precio { color: var(--color-success); font-weight: 700; margin: 0 0 4px; }
.desc { font-size: 12px; color: var(--color-muted); margin: 0; }

@media print {
  .page-header button,
  .card:has(input),
  .sidebar,
  .app-header {
    display: none !important;
  }
}
</style>
