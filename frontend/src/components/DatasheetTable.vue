<template>
  <div class="datasheet-table">
    <!-- Filtros -->
    <div class="table-controls">
      <div class="search-box">
        <span class="p-input-icon-left search-field">
          <i class="pi pi-search" />
          <InputText
            v-model="searchTerm"
            placeholder="Buscar..."
            @input="onSearchChange"
          />
        </span>
      </div>
      
      <div class="table-info">
        <i class="pi pi-info-circle"></i>
        Total: {{ data?.pagination?.total_records || 0 }} registros
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="table-loading">
      <i class="pi pi-spin pi-spinner"></i>
      <p>Carregando dados...</p>
    </div>

    <!-- Erro -->
    <div v-else-if="error" class="table-error">
      <i class="pi pi-exclamation-triangle"></i>
      <p>Erro ao carregar dados: {{ error }}</p>
    </div>

    <!-- Tabela -->
    <div v-else-if="data" class="table-wrapper">
      <DataTable
        :value="data.data"
        :paginator="false"
        :rows="pageSize"
        :rowsPerPageOptions="[10, 25, 50, 100]"
        responsiveLayout="scroll"
        :sortField="sortBy"
        :sortOrder="sortOrder === 'asc' ? 1 : -1"
        @sort="onSort"
        stripedRows
        class="p-datatable-sm"
      >
        <Column
          v-for="col in data.columns"
          :key="col"
          :field="col"
          :header="formatColumnName(col)"
          :sortable="true"
          class="th"
        >
          <template #body="{ data }">
            {{ formatCellValue(data[col]) }}
          </template>
        </Column>
      </DataTable>

      <!-- Paginação customizada -->
      <div class="custom-pagination">
        <div class="pagination-info">
          Página {{ data.pagination.page }} de {{ data.pagination.total_pages }}
          ({{ data.pagination.total_records }} registros)
        </div>
        
        <div class="pagination-controls">
          <Button
            icon="pi pi-angle-double-left"
            @click="goToPage(1)"
            :disabled="page === 1"
            class="p-button-sm p-button-text"
          />
          <Button
            icon="pi pi-angle-left"
            @click="goToPage(page - 1)"
            :disabled="page === 1"
            class="p-button-sm p-button-text"
          />
          
          <span class="page-input">
            <InputText
              v-model.number="currentPageInput"
              @keypress.enter="goToInputPage"
              type="number"
              :min="1"
              :max="data.pagination.total_pages"
            />
          </span>
          
          <Button
            icon="pi pi-angle-right"
            @click="goToPage(page + 1)"
            :disabled="page >= data.pagination.total_pages"
            class="p-button-sm p-button-text"
          />
          <Button
            icon="pi pi-angle-double-right"
            @click="goToPage(data.pagination.total_pages)"
            :disabled="page >= data.pagination.total_pages"
            class="p-button-sm p-button-text"
          />
        </div>

        <div class="page-size-control">
          <label>Registros por página:</label>
          <Dropdown
            v-model="pageSize"
            :options="[10, 25, 50, 100]"
            @change="onPageSizeChange"
          />
        </div>
      </div>
    </div>

    <!-- Vazio -->
    <div v-else class="table-empty">
      <i class="pi pi-inbox"></i>
      <p>Nenhum registro encontrado</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import { getTableData } from '../api/client'

const props = defineProps({
  tableName: {
    type: String,
    required: true,
  },
})

// Estado
const page = ref(1)
const pageSize = ref(50)
const searchTerm = ref('')
const sortBy = ref('')
const sortOrder = ref('asc')
const currentPageInput = ref(1)

// Debounce do search
let searchTimeout = null
const debouncedSearch = ref('')

const onSearchChange = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    debouncedSearch.value = searchTerm.value
    page.value = 1 // Volta para primeira página ao buscar
  }, 500)
}

// Query dos dados
const {
  data,
  isLoading,
  error,
} = useQuery({
  queryKey: ['tableData', props.tableName, page, pageSize, debouncedSearch, sortBy, sortOrder],
  queryFn: () =>
    getTableData({
      table_name: props.tableName,
      page: page.value,
      page_size: pageSize.value,
      search: debouncedSearch.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
    }),
  keepPreviousData: true,
})

// Watchers
watch(page, (newPage) => {
  currentPageInput.value = newPage
})

// Métodos
const goToPage = (newPage) => {
  if (newPage >= 1 && newPage <= data.value?.pagination?.total_pages) {
    page.value = newPage
  }
}

const goToInputPage = () => {
  goToPage(currentPageInput.value)
}

const onPageSizeChange = () => {
  page.value = 1
}

const onSort = (event) => {
  sortBy.value = event.sortField
  sortOrder.value = event.sortOrder === 1 ? 'asc' : 'desc'
}

const formatColumnName = (col) => {
  // Formata o nome da coluna para ficar mais legível
  return col
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const formatCellValue = (value) => {
  if (value === null || value === undefined) {
    return '-'
  }
  if (typeof value === 'number') {
    return value.toLocaleString('pt-BR')
  }
  if (typeof value === 'boolean') {
    return value ? 'Sim' : 'Não'
  }
  return value
}
</script>

<style scoped>
.datasheet-table {
  margin-top: 1rem;
}

.table-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.search-box {
  flex: 1;
  max-width: 400px;
}

.th div.p-column-header-content,.search-field {
    display: inline-flex;
    gap: 0.5rem;
}

.table-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
  font-size: 0.95rem;
}

.table-loading,
.table-error,
.table-empty {
  text-align: center;
  padding: 3rem 2rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.table-loading i,
.table-error i,
.table-empty i {
  font-size: 3rem;
  margin-bottom: 1rem;
  display: block;
}

.table-loading i {
  color: #667eea;
}

.table-error i {
  color: #c33;
}

.table-empty i {
  color: #999;
}

.table-wrapper {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.custom-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
  flex-wrap: wrap;
  gap: 1rem;
}

.pagination-info {
  color: #666;
  font-size: 0.9rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-input {
  display: inline-flex;
  align-items: center;
}

.page-input input {
  width: 60px;
  text-align: center;
}

.page-size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.page-size-control label {
  color: #666;
}

/* Responsivo */
@media (max-width: 768px) {
  .table-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    max-width: 100%;
  }

  .custom-pagination {
    flex-direction: column;
    text-align: center;
  }
}
</style>
