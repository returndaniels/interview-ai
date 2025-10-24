<template>
  <div class="chat-view container">
    <div class="chat-header">
      <h1><i class="pi pi-comments"></i> Chat com IA</h1>
      <p>Faça perguntas sobre seus datasheets e receba respostas em tempo real</p>
    </div>

    <div class="chat-container">
      <div class="messages-area" ref="messagesArea">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.type]"
        >
          <div class="message-icon">
            <i :class="message.type === 'user' ? 'pi pi-user' : 'pi pi-robot'"></i>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(message.text)"></div>
            <div v-if="message.sql" class="message-sql">
              <strong>SQL:</strong>
              <pre>{{ message.sql }}</pre>
            </div>
            <div v-if="message.explanation" class="message-explanation">
              <strong>Explicação:</strong> {{ message.explanation }}
            </div>
          </div>
        </div>

        <div v-if="isProcessing" class="message assistant processing">
          <div class="message-icon">
            <i class="pi pi-spin pi-spinner"></i>
          </div>
          <div class="message-content">
            <div class="message-text">{{ processingStatus }}</div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <div class="connection-status" :class="{ connected: isConnected }">
          <i :class="isConnected ? 'pi pi-check-circle' : 'pi pi-times-circle'"></i>
          {{ isConnected ? 'Conectado' : 'Desconectado' }}
        </div>
        
        <div class="input-group">
          <input
            v-model="question"
            @keypress.enter="sendQuestion"
            type="text"
            placeholder="Digite sua pergunta sobre os datasheets..."
            :disabled="!isConnected || isProcessing"
            class="question-input"
          />
          <button
            @click="sendQuestion"
            :disabled="!isConnected || isProcessing || !question.trim()"
            class="send-button"
          >
            <i class="pi pi-send"></i>
            Enviar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

const messages = ref([])
const question = ref('')
const isConnected = ref(false)
const isProcessing = ref(false)
const processingStatus = ref('Processando...')
const messagesArea = ref(null)

let ws = null

const connectWebSocket = () => {
  ws = new WebSocket(`${WS_URL}/ws/query`)

  ws.onopen = () => {
    isConnected.value = true
    console.log('WebSocket connected')
  }

  ws.onclose = () => {
    isConnected.value = false
    console.log('WebSocket disconnected')
    // Reconecta após 3 segundos
    setTimeout(connectWebSocket, 3000)
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    handleWebSocketMessage(data)
  }
}

const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'connected':
      // Conexão estabelecida
      break

    case 'loading_tables':
      processingStatus.value = 'Carregando tabelas...'
      break

    case 'tables_loaded':
      processingStatus.value = `${data.count} tabelas carregadas`
      break

    case 'building_context':
      processingStatus.value = 'Construindo contexto...'
      break

    case 'generating_sql':
      processingStatus.value = 'Gerando consulta SQL...'
      break

    case 'sql_generated':
      processingStatus.value = 'SQL gerado, executando...'
      break

    case 'executing_sql':
      processingStatus.value = 'Executando consulta...'
      break

    case 'sql_executed':
      processingStatus.value = `${data.results_count} resultados encontrados`
      break

    case 'humanizing':
      processingStatus.value = 'Gerando resposta...'
      break

    case 'response':
      isProcessing.value = false
      messages.value.push({
        type: 'assistant',
        text: data.humanized_response,
        sql: data.sql_query,
        explanation: data.sql_explanation,
      })
      scrollToBottom()
      break

    case 'error':
      isProcessing.value = false
      messages.value.push({
        type: 'error',
        text: data.message || 'Ocorreu um erro ao processar sua pergunta',
      })
      scrollToBottom()
      break

    case 'end':
      isProcessing.value = false
      break
  }
}

const sendQuestion = () => {
  if (!question.value.trim() || !isConnected.value || isProcessing.value) {
    return
  }

  // Adiciona mensagem do usuário
  messages.value.push({
    type: 'user',
    text: question.value,
  })

  // Envia pergunta pelo WebSocket
  ws.send(JSON.stringify({ question: question.value }))

  isProcessing.value = true
  processingStatus.value = 'Processando...'
  question.value = ''
  
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesArea.value) {
      messagesArea.value.scrollTop = messagesArea.value.scrollHeight
    }
  })
}

const formatMessage = (text) => {
  // Converte markdown básico para HTML
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})
</script>

<style scoped>
.chat-view {
  padding: 2rem;
}

.chat-header {
  margin-bottom: 2rem;
}

.chat-header h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.chat-header p {
  color: #666;
  font-size: 1.1rem;
}

.chat-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  height: calc(100vh - 250px);
  display: flex;
  flex-direction: column;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message {
  display: flex;
  gap: 1rem;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.2rem;
}

.message.user .message-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message.assistant .message-icon {
  background: #f0f0f0;
  color: #667eea;
}

.message.error .message-icon {
  background: #fee;
  color: #c33;
}

.message.processing .message-icon {
  background: #f0f0f0;
  color: #667eea;
}

.message-content {
  flex: 1;
  padding: 1rem;
  border-radius: 12px;
  background: #f8f9fa;
}

.message.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message.error .message-content {
  background: #fee;
  color: #c33;
}

.message-text {
  line-height: 1.6;
}

.message-sql {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  font-size: 0.9rem;
}

.message-sql pre {
  margin-top: 0.5rem;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Courier New', monospace;
}

.message-explanation {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 0.9rem;
  opacity: 0.9;
}

.input-area {
  padding: 1.5rem;
  border-top: 1px solid #e0e0e0;
  background: #fafafa;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #c33;
}

.connection-status.connected {
  color: #2c3;
}

.input-group {
  display: flex;
  gap: 1rem;
}

.question-input {
  flex: 1;
  padding: 0.875rem 1.25rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.question-input:focus {
  outline: none;
  border-color: #667eea;
}

.question-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.send-button {
  padding: 0.875rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
