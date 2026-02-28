/**
 * useAuth.js — Composable placeholder para autenticación y roles.
 *
 * LISTO PARA IMPLEMENTAR:
 * Cuando se requiera auth, descomentar y completar las funciones.
 * El sistema de roles soporta: 'admin' | 'cajero' | 'solo_lectura'
 *
 * Integración sugerida:
 *  - Backend: agregar JWT en FastAPI con librería `python-jose`
 *  - Endpoint: POST /auth/login → devuelve token
 *  - Frontend: guardar token en localStorage, enviarlo como Bearer en axios
 */

import { ref, computed } from 'vue'

// ── Estado global de auth (singleton) ──────────────────────────────────────
const usuario = ref(null)  // { id, nombre, rol: 'admin'|'cajero'|'solo_lectura' }
const token = ref(null)

// ── Composable ──────────────────────────────────────────────────────────────
export function useAuth() {
    const estaAutenticado = computed(() => !!usuario.value)
    const rol = computed(() => usuario.value?.rol ?? null)
    const nombre = computed(() => usuario.value?.nombre ?? 'Invitado')

    // Permisos por rol
    const puede = {
        verDashboard: computed(() => true),  // todos
        vender: computed(() => true),  // todos
        editarProductos: computed(() => true),  // cuando haya auth: rol.value !== 'solo_lectura'
        anularVentas: computed(() => true),  // cuando haya auth: ['admin'].includes(rol.value)
        ajustarStock: computed(() => true),  // cuando haya auth: ['admin'].includes(rol.value)
        verReportes: computed(() => true),  // todos
    }

    /**
     * Login — reemplazar con llamada real al backend
     * @param {string} _usuario
     * @param {string} _password
     */
    async function login(_usuario, _password) {
        // TODO: implementar cuando el backend tenga auth
        // const res = await apiClient.post('/auth/login', { usuario: _usuario, password: _password })
        // token.value = res.data.access_token
        // usuario.value = res.data.usuario
        // localStorage.setItem('auth_token', token.value)
        throw new Error('Auth no implementado todavía')
    }

    function logout() {
        usuario.value = null
        token.value = null
        localStorage.removeItem('auth_token')
    }

    /**
     * Verificar si hay sesión guardada al cargar la app
     * Llamar desde main.js o App.vue: await checkSesion()
     */
    async function checkSesion() {
        // TODO: implementar verificación de token guardado
        // const savedToken = localStorage.getItem('auth_token')
        // if (savedToken) { ... verificar con backend }
    }

    return { usuario, token, estaAutenticado, rol, nombre, puede, login, logout, checkSesion }
}
