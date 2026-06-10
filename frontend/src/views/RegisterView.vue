<template>
  <div class="card">
    <h1>Rejestracja</h1>
    <div class="form-group">
      <label>Nazwa użytkownika</label>
      <input v-model="username" type="text" placeholder="Wybierz nazwę użytkownika" />
    </div>
    <div class="form-group">
      <label>Hasło</label>
      <input v-model="password" type="password" placeholder="Wybierz hasło" />
    </div>
    <div class="form-group">
      <label>Powtórz hasło</label>
      <input v-model="confirmPassword" type="password" placeholder="Powtórz hasło" />
    </div>
    <button @click="handleRegister" :disabled="loading || !isValid">
      {{ loading ? 'Rejestracja...' : 'Zarejestruj się' }}
    </button>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="success" class="success">{{ success }}</div>

    <div class="links">
      <p>Masz już konto? <router-link to="/login">Zaloguj się</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

const isValid = computed(() => {
  return username.value && password.value && password.value === confirmPassword.value
})

async function handleRegister() {
  if (password.value !== confirmPassword.value) {
    error.value = 'Hasła nie są identyczne'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const result = await authStore.register(username.value, password.value)
    authStore.setToken(result.token)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Błąd rejestracji'
  } finally {
    loading.value = false
  }
}
</script>
