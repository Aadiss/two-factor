<template>
  <div class="card">
    <h1>Konfiguracja aplikacji autentykującej</h1>

    <div v-if="!verified">
      <div v-if="!qrCode">
        <p>Kliknij poniższy przycisk, aby wygenerować kod QR dla aplikacji autentykującej.</p>
        <button @click="setupTOTP" :disabled="loading">
          {{ loading ? 'Generowanie...' : 'Wygeneruj kod QR' }}
        </button>
      </div>

      <div v-else>
        <p>Zeskanuj ten kod QR za pomocą aplikacji autentykującej (Microsoft Authenticator, Google Authenticator itp.):</p>
        <div class="qr-code">
          <img :src="'data:image/png;base64,' + qrCode" alt="Kod QR" />
        </div>

        <p style="font-size: 12px; color: #666; word-break: break-all;">
          Ręczny klucz wprowadzania: <strong>{{ secret }}</strong>
        </p>

        <div class="form-group" style="margin-top: 16px;">
          <label>Wprowadź 6-cyfrowy kod z aplikacji, aby zweryfikować</label>
          <input v-model="code" type="text" placeholder="000000" maxlength="6" />
        </div>
        <button @click="verifyTOTP" :disabled="loading || code.length !== 6">
          {{ loading ? 'Weryfikacja...' : 'Zweryfikuj i włącz' }}
        </button>
      </div>
    </div>

    <div v-else>
      <div class="success">Aplikacja autentykująca została włączona!</div>
      <router-link to="/dashboard">
        <button style="margin-top: 16px;">Powrót do pulpitu</button>
      </router-link>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div style="margin-top: 16px;">
      <router-link to="/dashboard">
        <button class="secondary">Anuluj</button>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const qrCode = ref('')
const secret = ref('')
const code = ref('')
const verified = ref(false)
const loading = ref(false)
const error = ref('')

async function setupTOTP() {
  loading.value = true
  error.value = ''

  try {
    const { data } = await api.post('/2fa/totp/setup')
    qrCode.value = data.qr_code
    secret.value = data.secret
  } catch (e) {
    error.value = e.response?.data?.detail || 'Nie udało się skonfigurować TOTP'
  } finally {
    loading.value = false
  }
}

async function verifyTOTP() {
  loading.value = true
  error.value = ''

  try {
    await api.post('/2fa/totp/verify', { code: code.value })
    verified.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || 'Nieprawidłowy kod'
  } finally {
    loading.value = false
  }
}
</script>
