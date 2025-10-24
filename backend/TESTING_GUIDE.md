# Guia de Testes - Query SQL com IA

## 🎯 Funcionalidade

O sistema usa OpenAI para:
1. **Gerar query SQL** baseada em perguntas em linguagem natural
2. **Executar a query** de forma segura (somente SELECT)
3. **Humanizar resultados** transformando dados em respostas claras

---

## 🔒 Segurança

### Validações Implementadas:

✅ **Apenas queries SELECT permitidas**  
✅ **Bloqueio de comandos perigosos**: INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE, etc.  
✅ **Sem múltiplos statements** (evita SQL injection com `;`)  
✅ **Sem comentários maliciosos**  
✅ **Validação dupla**: IA gera + validador verifica  

---

## 📡 Endpoints Disponíveis

### 1. **HTTP POST - `/query/{table_name}`**

Gera SQL, executa e retorna resposta humanizada completa.

#### Exemplo cURL:
```bash
curl -X POST "http://localhost:8000/query/minha_tabela?question=Qual%20a%20m%C3%A9dia%20de%20vendas?" \
  -H "Content-Type: application/json"
```

#### Response:
```json
{
  "question": "Quantos funcionários ganham mais de 5000?",
  "sql_query": "SELECT COUNT(*) as total FROM `employees` WHERE salary > 5000",
  "sql_explanation": "Esta query conta quantos funcionários têm salário maior que 5000",
  "results_count": 1,
  "humanized_response": "Existem 42 funcionários que ganham mais de R$ 5.000,00.",
  "raw_results": [{"total": 42}]
}
```

---

### 2. **WebSocket - `/ws/query/{table_name}`**

Mesmo fluxo, mas com feedback em tempo real de cada etapa.

---

## 🧪 Exemplos de Perguntas

### **Agregações Simples:**
- "Qual a média de vendas?"
- "Quantos registros existem?"
- "Qual o total de receita?"

### **Filtros:**
- "Quantos clientes são do Brasil?"
- "Mostre vendas acima de 1000"

### **Agrupamentos:**
- "Média salarial por departamento"
- "Total de vendas por mês"

---

## ❌ Testes de Segurança

### **Teste 1: Tentativa de DELETE**
```bash
curl -X POST "http://localhost:8000/query/users?question=DELETE%20FROM%20users"
```
**Resultado Esperado:**
```json
{
  "detail": "Query inválida ou insegura: Query contém comando proibido: DELETE"
}
```

### **Teste 2: SQL Injection**
```bash
curl -X POST "http://localhost:8000/query/users?question=SELECT%20*;%20DROP%20TABLE%20users"
```
**Resultado Esperado:**
```json
{
  "detail": "Query inválida ou insegura: Múltiplas queries não são permitidas"
}
```
