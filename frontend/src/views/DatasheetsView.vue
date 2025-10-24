<template>
  <div class="datasheets-view container">
    <div class="datasheets-header">
      <div>
        <h1><i class="pi pi-table"></i> Datasheets</h1>
        <p>Visualize e gerencie seus datasheets importados</p>
      </div>
      <Button
        label="Upload Datasheet"
        icon="pi pi-upload"
        @click="showUploadDialog = true"
        class="p-button-success upload-button"
      />
    </div>

    <div v-if="tablesLoading" class="loading-state">
      <i class="pi pi-spin pi-spinner"></i>
      <p>Carregando datasheets...</p>
    </div>

    <div v-else-if="tablesError" class="error-state">
      <i class="pi pi-exclamation-triangle"></i>
      <p>Erro ao carregar datasheets: {{ tablesError }}</p>
    </div>

    <div v-else-if="tables.length === 0" class="empty-state">
      <i class="pi pi-inbox"></i>
      <p>Nenhum datasheet encontrado</p>
      <Button
        label="Upload seu primeiro datasheet"
        icon="pi pi-upload"
        @click="showUploadDialog = true"
        class="upload-button"
      />
    </div>

    <div v-else class="datasheets-content">
      <TabView v-model:activeIndex="activeTabIndex">
        <TabPanel
          v-for="table in tables"
          :key="table"
          :header="formatTableName(table)"
        >
          <DatasheetTable :tableName="table" />
        </TabPanel>
      </TabView>
    </div>

    <!-- Dialog de Upload -->
    <Dialog
      v-model:visible="showUploadDialog"
      header="Upload Datasheet"
      :modal="true"
      :style="{ width: '500px' }"
    >
      <div class="upload-form">
        <div class="form-field">
          <label for="file">Arquivo Excel (.xlsx ou .xls)</label>
          <input
            type="file"
            id="file"
            accept=".xlsx,.xls"
            @change="onFileSelect"
            ref="fileInput"
          />
        </div>

        <div class="form-field">
          <label for="tableName">Nome da Tabela (opcional)</label>
          <InputText
            id="tableName"
            v-model="tableName"
            placeholder="Deixe vazio para usar o nome do arquivo"
          />
        </div>

        <div v-if="uploadError" class="upload-error">
          <i class="pi pi-exclamation-circle"></i>
          {{ uploadError }}
        </div>

        <div v-if="uploadSuccess" class="upload-success">
          <i class="pi pi-check-circle"></i>
          Upload realizado com sucesso!
        </div>
      </div>

      <template #footer>
        <Button
          label="Cancelar"
          icon="pi pi-times"
          @click="closeUploadDialog"
          class="p-button-text"
        />
        <Button
          label="Upload"
          icon="pi pi-upload"
          @click="uploadFile"
          :loading="uploading"
          :disabled="!selectedFile"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import Button from 'primevue/button'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import DatasheetTable from '../components/DatasheetTable.vue'
import { getTables, uploadExcel } from '../api/client'

const queryClient = useQueryClient()

// Estado das abas
const activeTabIndex = ref(0)

// Query de tabelas
const {
  data: tablesData,
  isLoading: tablesLoading,
  error: tablesError,
} = useQuery({
  queryKey: ['tables'],
  queryFn: getTables,
})

const tables = computed(() => tablesData.value?.tables || [])

// Upload
const showUploadDialog = ref(false)
const selectedFile = ref(null)
const tableName = ref('')
const uploading = ref(false)
const uploadError = ref(null)
const uploadSuccess = ref(false)
const fileInput = ref(null)

const onFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    uploadError.value = null
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  uploadError.value = null
  uploadSuccess.value = false

  try {
    await uploadExcel(selectedFile.value, tableName.value || null)
    uploadSuccess.value = true
    
    // Recarrega lista de tabelas
    setTimeout(() => {
      queryClient.invalidateQueries(['tables'])
      closeUploadDialog()
    }, 1500)
  } catch (error) {
    uploadError.value = error.response?.data?.detail || 'Erro ao fazer upload'
  } finally {
    uploading.value = false
  }
}

const closeUploadDialog = () => {
  showUploadDialog.value = false
  selectedFile.value = null
  tableName.value = ''
  uploadError.value = null
  uploadSuccess.value = false
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatTableName = (tableName) => {
  // Remove o prefixo datasheet_ e capitaliza
  return tableName
    .replace('datasheet_', '')
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
</script>

<style scoped>
.datasheets-view {
  padding: 2rem;
}

.datasheets-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.datasheets-header h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.datasheets-header p {
  color: #666;
  font-size: 1.1rem;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.loading-state i,
.error-state i,
.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  display: block;
}

.loading-state i {
  color: #667eea;
}

.error-state i {
  color: #c33;
}

.empty-state i {
  color: #999;
}

.loading-state p,
.error-state p,
.empty-state p {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 1rem;
}

.datasheets-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.upload-button {
    display: inline-flex;
    gap: 0.5rem;
    padding: 1rem 2rem;
}

.upload-form {
  padding: 1rem 0;
}

.form-field {
  margin-bottom: 1.5rem;
}

.form-field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.form-field input[type="file"] {
  width: 100%;
  padding: 0.5rem;
  border: 2px dashed #ddd;
  border-radius: 8px;
  cursor: pointer;
}

.upload-error {
  padding: 1rem;
  background: #fee;
  color: #c33;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.upload-success {
  padding: 1rem;
  background: #efe;
  color: #2c3;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
}
</style>
