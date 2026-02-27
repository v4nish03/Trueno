<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="sidebar-logo">
      <div class="logo-icon">⚡</div>
      <div class="logo-text">
        <span class="logo-name">Trueno</span>
        <span class="logo-sub">Motors</span>
      </div>
    </div>

    <!-- Alertas globales -->
    <div v-if="alertasStore.totalStockBajo > 0 || alertasStore.totalSinStock > 0" class="sidebar-alerts">
      <div v-if="alertasStore.totalStockBajo > 0" class="sidebar-alert warning">
        <span>⚠️</span>
        <span>{{ alertasStore.totalStockBajo }} con stock bajo</span>
      </div>
      <div v-if="alertasStore.totalSinStock > 0" class="sidebar-alert danger">
        <span>🚨</span>
        <span>{{ alertasStore.totalSinStock }} sin stock</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <router-link v-for="item in navItems" :key="item.to" :to="item.to" class="nav-item">
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
        <span v-if="item.badge && item.badge > 0" class="nav-badge">{{ item.badge }}</span>
      </router-link>
    </nav>

    <!-- Footer -->
    <div class="sidebar-footer">
      <div class="status-dot"></div>
      <span>Sistema activo</span>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useAlertasStore } from '@/stores/alertas'

const alertasStore = useAlertasStore()

const navItems = computed(() => [
  { to: '/dashboard', icon: '🏠', label: 'Dashboard' },
  { to: '/pos', icon: '🛒', label: 'Punto de Venta' },
  { to: '/productos', icon: '📦', label: 'Productos' },
  { to: '/movimientos', icon: '📊', label: 'Movimientos' },
  { to: '/ventas', icon: '💰', label: 'Ventas', badge: 0 },
])
</script>

<style scoped>
.sidebar {
  width: 220px;
  min-width: 220px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: 20px 12px;
  gap: 8px;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 8px 16px;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 8px;
}
.logo-icon {
  font-size: 24px;
  line-height: 1;
}
.logo-name {
  display: block;
  font-size: 16px;
  font-weight: 800;
  color: var(--color-accent);
  line-height: 1;
}
.logo-sub {
  display: block;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-muted);
}

.sidebar-alerts {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 4px;
}
.sidebar-alert {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
}
.sidebar-alert.warning {
  background: rgba(245,158,11,0.1);
  color: #f59e0b;
  border: 1px solid rgba(245,158,11,0.2);
}
.sidebar-alert.danger {
  background: rgba(239,68,68,0.1);
  color: #ef4444;
  border: 1px solid rgba(239,68,68,0.2);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 8px;
  color: var(--color-muted);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s;
  position: relative;
}
.nav-item:hover {
  background: var(--color-surface-2);
  color: var(--color-text);
}
.nav-item.router-link-active {
  background: rgba(108, 99, 255, 0.12);
  color: var(--color-accent);
  border: 1px solid rgba(108,99,255,0.2);
}
.nav-icon { font-size: 16px; }
.nav-label { flex: 1; }
.nav-badge {
  background: var(--color-danger);
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.sidebar-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px 4px;
  border-top: 1px solid var(--color-border);
  font-size: 11px;
  color: var(--color-muted);
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-success);
  box-shadow: 0 0 6px var(--color-success);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
