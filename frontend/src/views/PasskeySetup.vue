<template>
  <div class="card">
    <h1>Konfiguracja kluczy bezpieczeństwa</h1>

    <div class="form-group">
      <label>Nazwa urządzenia (opcjonalnie)</label>
      <input v-model="deviceName" type="text" placeholder="np. YubiKey 5" />
    </div>

    <button @click="registerPasskey" :disabled="loading">
      {{ loading ? 'Oczekiwanie na klucz bezpieczeństwa...' : 'Zarejestruj klucz bezpieczeństwa' }}
    </button>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="success" class="success">{{ success }}</div>

    <div v-if="passkeys.length > 0" class="passkey-list">
      <h2>Zarejestrowane klucze</h2>
      <div v-for="pk in passkeys" :key="pk.credential_id" class="passkey-item">
        <div class="passkey-info">
          <div class="passkey-name">{{ pk.device_name || 'Klucz bezpieczeństwa' }}</div>
          <div class="passkey-date">Dodano: {{ new Date(pk.created_at).toLocaleDateString() }}</div>
        </div>
        <button class="danger" style="width: auto; padding: 6px 12px;" @click="removePasskey(pk.credential_id)">
          Usuń
        </button>
      </div>
    </div>

    <div style="margin-top: 16px;">
      <router-link to="/dashboard">
        <button class="secondary">Powrót do pulpitu</button>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { startRegistration } from '@simplewebauthn/browser'

const deviceName = ref('')
const passkeys = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')

onMounted(async () => {
  await loadPasskeys()
})

async function loadPasskeys() {
  try {
    const { data } = await api.get('/2fa/passkey/list')
    passkeys.value = data
  } catch (e) {
    error.value = 'Nie udało się załadować kluczy'
  }
}

async function registerPasskey() {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const { data: options } = await api.post('/2fa/passkey/register/begin')

    const credential = await startRegistration(options.options)

    await api.post('/2fa/passkey/register/complete', {
      id: credential.id,
      rawId: credential.rawId,
      response: credential.response,
      state: options.state
    })

    success.value = 'Klucz bezpieczeństwa został zarejestrowany!'
    await loadPasskeys()
    deviceName.value = ''
  } catch (e) {
    error.value = e.response?.data?.detail || 'Rejestracja klucza nie powiodła się'
  } finally {
    loading.value = false
  }
}

async function removePasskey(credentialId) {
  if (!confirm('Usunąć ten klucz bezpieczeństwa?')) return

  try {
    await api.delete(`/2fa/passkey/${credentialId}`)
    await loadPasskeys()
    success.value = 'Klucz bezpieczeństwa został usunięty'
  } catch (e) {
    error.value = 'Nie udało się usunąć klucza'
  }
}
</script>
