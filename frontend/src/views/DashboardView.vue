<template>
  <div class="card">
    <h1>Pulpit</h1>

    <div v-if="user">
      <p><strong>Nazwa użytkownika:</strong> {{ user.username }}</p>

      <div v-if="!user.totp_enabled && !user.has_passkeys" class="status warning">
        Twoje konto nie jest chronione uwierzytelnianiem dwuskładnikowym. Zalecamy skonfigurowanie jednej z poniższych metod.
      </div>

      <h2 style="margin-top: 24px;">Uwierzytelnianie dwuskładnikowe</h2>

      <div class="status" :class="user.totp_enabled ? 'enabled' : 'disabled'">
        Aplikacja autentykująca: {{ user.totp_enabled ? 'Włączona' : 'Nie skonfigurowana' }}
      </div>

      <div class="status" :class="user.has_passkeys ? 'enabled' : 'disabled'">
        Klucze bezpieczeństwa: {{ user.has_passkeys ? 'Włączone' : 'Nie skonfigurowane' }}
      </div>

      <div style="margin-top: 20px;">
        <router-link to="/setup/totp">
          <button>{{ user.totp_enabled ? 'Zarządzaj' : 'Skonfiguruj' }} aplikacją autentykującą</button>
        </router-link>
        <router-link to="/setup/passkey">
          <button class="secondary">{{ user.has_passkeys ? 'Zarządzaj' : 'Skonfiguruj' }} kluczami bezpieczeństwa</button>
        </router-link>
      </div>
    </div>

    <button class="danger" @click="logout" style="margin-top: 24px;">Wyloguj się</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const user = ref(null)

onMounted(async () => {
  try {
    user.value = await authStore.fetchUser()
  } catch {
    router.push('/login')
  }
})

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>
