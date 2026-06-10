<template>
  <div class="card">
    <h1>Logowanie</h1>

    <div v-if="!show2FA">
      <div class="form-group">
        <label>Nazwa użytkownika</label>
        <input v-model="username" type="text" placeholder="Wprowadź nazwę użytkownika" />
      </div>
      <div class="form-group">
        <label>Hasło</label>
        <input v-model="password" type="password" placeholder="Wprowadź hasło" />
      </div>
      <button @click="handleLogin" :disabled="loading">
        {{ loading ? 'Logowanie...' : 'Zaloguj się' }}
      </button>
    </div>

    <div v-else>
      <div v-if="pending2FA?.totp_enabled" class="form-group">
        <label>Wprowadź 6-cyfrowy kod z aplikacji autentykującej</label>
        <input v-model="totpCode" type="text" placeholder="000000" maxlength="6" />
        <button @click="verifyTOTP" :disabled="loading || totpCode.length !== 6">
          {{ loading ? 'Weryfikacja...' : 'Zweryfikuj kod' }}
        </button>
      </div>

      <div v-if="pending2FA?.has_passkeys">
        <button @click="authenticatePasskey" :disabled="loading">
          {{ loading ? 'Oczekiwanie na klucz bezpieczeństwa...' : 'Użyj klucza bezpieczeństwa' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="success" class="success">{{ success }}</div>

    <div class="links">
      <p>Nie masz konta? <router-link to="/register">Zarejestruj się</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
import { startAuthentication } from '@simplewebauthn/browser'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const totpCode = ref('')
const show2FA = ref(false)
const loading = ref(false)
const error = ref('')
const success = ref('')
const pending2FA = ref(null)

async function handleLogin() {
  loading.value = true
  error.value = ''

  try {
    const result = await authStore.login(username.value, password.value)

    if (result.requires_2fa) {
      pending2FA.value = authStore.pending2FA
      show2FA.value = true
    } else {
      router.push('/dashboard')
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Błąd logowania'
  } finally {
    loading.value = false
  }
}

async function verifyTOTP() {
  loading.value = true
  error.value = ''

  try {
    const { data } = await api.post('/2fa/totp/validate', { code: totpCode.value }, {
      headers: { Authorization: `Bearer ${authStore.tempToken}` }
    })

    authStore.setToken(data.token)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Nieprawidłowy kod'
  } finally {
    loading.value = false
  }
}

async function authenticatePasskey() {
  loading.value = true
  error.value = ''

  try {
    const { data: options } = await api.post('/2fa/passkey/authenticate/begin', {}, {
      headers: { Authorization: `Bearer ${authStore.tempToken}` }
    })

    const credential = await startAuthentication(options.options)

    const { data } = await api.post('/2fa/passkey/authenticate/complete', {
      id: credential.id,
      rawId: credential.rawId,
      response: credential.response,
      state: options.state
    }, {
      headers: { Authorization: `Bearer ${authStore.tempToken}` }
    })

    authStore.setToken(data.token)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Uwierzytelnianie kluczem nie powiodło się'
  } finally {
    loading.value = false
  }
}
</script>
