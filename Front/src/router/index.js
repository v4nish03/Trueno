import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        component: () => import('@/components/layout/AppLayout.vue'),
        children: [
            { path: '', redirect: '/dashboard' },
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('@/views/DashboardView.vue'),
                meta: { title: 'Dashboard' }
            },
            {
                path: 'productos',
                name: 'Productos',
                component: () => import('@/views/ProductosView.vue'),
                meta: { title: 'Productos' }
            },
            {
                path: 'pos',
                name: 'POS',
                component: () => import('@/views/PosView.vue'),
                meta: { title: 'Punto de Venta' }
            },
            {
                path: 'movimientos',
                name: 'Movimientos',
                component: () => import('@/views/MovimientosView.vue'),
                meta: { title: 'Movimientos' }
            },
            {
                path: 'ventas',
                name: 'Ventas',
                component: () => import('@/views/VentasView.vue'),
                meta: { title: 'Historial de Ventas' }
            },
            {
                path: 'catalogo',
                name: 'Catalogo',
                component: () => import('@/views/CatalogoView.vue'),
                meta: { title: 'Catálogo' }
            },
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.afterEach((to) => {
    document.title = to.meta.title ? `${to.meta.title} — Trueno Motors` : 'Trueno Motors'
})

// Manejo de errores de carga de chunks (fragmentos JS) por caché antigua
router.onError((error, to) => {
    if (error.message.includes('Failed to fetch dynamically imported module') || error.message.includes('Importing a module script failed')) {
        // Forzar una recarga completa para obtener el nuevo index.html y los nuevos assets
        window.location.href = to.fullPath;
    }
})

export default router
