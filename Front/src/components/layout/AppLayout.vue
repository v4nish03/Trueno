<template>
  <div class="app-layout">
    <AppSidebar />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import AppSidebar from './AppSidebar.vue'
import { useAlertasStore } from '@/stores/alertas'
import { useCajaStore } from '@/stores/caja'

const alertasStore = useAlertasStore()
const cajaStore = useCajaStore()

onMounted(() => {
  alertasStore.iniciar()
  cajaStore.checkEstado()
})
onUnmounted(() => alertasStore.detener())
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 28px 32px;
  background: var(--color-bg);
}
</style>
