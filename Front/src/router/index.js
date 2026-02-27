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

export default router
