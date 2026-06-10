import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const tempToken = ref(null)
  const user = ref(null)
  const pending2FA = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  async function register(username, password) {
    const { data } = await api.post('/auth/register', { username, password })
    return data
  }

  async function login(username, password) {
    const { data } = await api.post('/auth/login', { username, password })

    if (data.requires_2fa) {
      tempToken.value = data.temp_token
      pending2FA.value = {
        totp_enabled: data.totp_enabled,
        has_passkeys: data.has_passkeys
      }
      return { requires_2fa: true }
    }

    token.value = data.token
    localStorage.setItem('token', data.token)
    user.value = data.user
    return { requires_2fa: false }
  }

  function setToken(newToken) {
    token.value = newToken
    tempToken.value = null
    pending2FA.value = null
    localStorage.setItem('token', newToken)
  }

  async function fetchUser() {
    const { data } = await api.get('/auth/me')
    user.value = data
    return data
  }

  function logout() {
    token.value = null
    tempToken.value = null
    user.value = null
    pending2FA.value = null
    localStorage.removeItem('token')
  }

  return {
    token, tempToken, user, pending2FA, isAuthenticated,
    register, login, setToken, fetchUser, logout
  }
})
