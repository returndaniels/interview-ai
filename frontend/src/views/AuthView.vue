<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-header">
        <h1><i class="pi pi-lock"></i> {{ isLogin ? 'Login' : 'Registro' }}</h1>
        <p>{{ isLogin ? 'Entre com sua conta' : 'Crie uma nova conta' }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-field">
          <label for="username">Username</label>
          <InputText
            id="username"
            v-model="username"
            placeholder="Digite seu username (uma palavra)"
            class="input-username"
            :class="{ 'p-invalid': errors.username }"
          />
          <small v-if="errors.username" class="p-error">{{ errors.username }}</small>
        </div>

        <div class="form-field">
          <label for="password">Senha</label>
          <Password
            id="password"
            v-model="password"
            placeholder="Digite sua senha"
            :feedback="!isLogin"
            toggleMask
            class="input-password"
            :class="{ 'p-invalid': errors.password }"
          />
          <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
        </div>

        <div v-if="error" class="error-message">
          <i class="pi pi-exclamation-circle"></i>
          {{ error }}
        </div>

        <Button
          type="submit"
          :label="isLogin ? 'Entrar' : 'Criar Conta'"
          :loading="loading"
          class="submit-button"
        />

        <div class="toggle-mode">
          <p>
            {{ isLogin ? 'Não tem uma conta?' : 'Já tem uma conta?' }}
            <a href="#" @click.prevent="toggleMode">
              {{ isLogin ? 'Registre-se' : 'Faça login' }}
            </a>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import { login, register } from '../api/client'

const router = useRouter()

const isLogin = ref(true)
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)
const errors = ref({})

const validateForm = () => {
  errors.value = {}

  if (!username.value) {
    errors.value.username = 'Username é obrigatório'
  } else if (username.value.includes(' ')) {
    errors.value.username = 'Username deve ser uma única palavra sem espaços'
  } else if (username.value.length < 3) {
    errors.value.username = 'Username deve ter pelo menos 3 caracteres'
  }

  if (!password.value) {
    errors.value.password = 'Senha é obrigatória'
  } else if (password.value.length < 6) {
    errors.value.password = 'Senha deve ter pelo menos 6 caracteres'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true
  error.value = null

  try {
    const authFunction = isLogin.value ? login : register
    const result = await authFunction(username.value, password.value)

    // Salva o token
    document.cookie = `token=${result.token}; path=/; max-age=${60 * 60 * 24 * 7}` // 7 dias

    // Redireciona para a página principal
    router.push('/datasheets')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erro ao autenticar'
  } finally {
    loading.value = false
  }
}

const toggleMode = () => {
  isLogin.value = !isLogin.value
  error.value = null
  errors.value = {}
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.auth-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 3rem;
  width: 100%;
  max-width: 450px;
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-header h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.auth-header p {
  color: #666;
  font-size: 1.1rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  font-weight: 600;
  color: #333;
}

.form-field input,
.form-field :deep(.p-password) {
  width: 100%;
}

:deep(.p-password.p-inputwrapper) {
    display: flex;
    align-items: center;
}

:deep(.p-password.p-inputwrapper .p-icon.p-input-icon)  {
    transform: translateY(-50%);
}

.input-username,
:deep(.p-password-input) {
  width: 100%;
  padding: 0.5rem;
}

.error-message {
  padding: 1rem;
  background: #fee;
  color: #c33;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.submit-button {
  width: 100%;
  padding: 0.75rem;
  font-size: 1.1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.submit-button:hover {
  background: linear-gradient(135deg, #5568d3 0%, #653a8a 100%);
}

.toggle-mode {
  text-align: center;
  color: #666;
}

.toggle-mode a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.toggle-mode a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .auth-container {
    padding: 2rem;
  }
}
</style>
