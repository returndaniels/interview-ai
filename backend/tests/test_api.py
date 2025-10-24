import pytest
from fastapi.testclient import TestClient
from app.main import app
import json
import io

client = TestClient(app)


class TestRootEndpoints:
    """Testes para endpoints básicos"""
    
    def test_root(self):
        """Testa endpoint raiz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Interview AI - Datasheet Importer API"
        assert data["status"] == "running"
        assert data["docs"] == "/docs"
    
    def test_health_check(self):
        """Testa health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data


class TestTablesEndpoints:
    """Testes para endpoints de tabelas"""
    
    def test_list_tables(self):
        """Testa listagem de tabelas"""
        response = client.get("/tables")
        assert response.status_code == 200
        data = response.json()
        assert "tables" in data
        assert "count" in data
        assert isinstance(data["tables"], list)
        assert data["count"] == len(data["tables"])
        
        # Verifica que todas as tabelas têm prefixo datasheet_
        for table in data["tables"]:
            assert table.startswith("datasheet_")


class TestUploadEndpoint:
    """Testes para upload de Excel"""
    
    def test_upload_invalid_extension(self):
        """Testa upload com extensão inválida"""
        # Cria arquivo fake com extensão errada
        fake_file = io.BytesIO(b"fake content")
        files = {"file": ("test.txt", fake_file, "text/plain")}
        
        response = client.post("/upload/excel", files=files)
        assert response.status_code == 400
        assert "Formato de arquivo inválido" in response.json()["detail"]
    
    def test_upload_without_file(self):
        """Testa upload sem arquivo"""
        response = client.post("/upload/excel")
        assert response.status_code == 422  # Unprocessable Entity


class TestQueryEndpoint:
    """Testes para endpoint de query"""
    
    def test_query_without_question(self):
        """Testa query sem pergunta"""
        response = client.post("/query")
        assert response.status_code == 422  # Missing required parameter
    
    def test_query_with_empty_question(self):
        """Testa query com pergunta vazia"""
        response = client.post("/query?question=")
        # Pode retornar 400 ou 503 dependendo do estado do banco
        assert response.status_code in [400, 503]
    
    def test_query_no_tables(self):
        """Testa query quando não há tabelas"""
        response = client.post("/query?question=teste")
        # Se não houver tabelas, deve retornar 503 ou executar normalmente
        assert response.status_code in [200, 503]
        
        if response.status_code == 503:
            assert "tabela" in response.json()["detail"].lower()


class TestWebSocketEndpoint:
    """Testes para WebSocket"""
    
    def test_websocket_connection(self):
        """Testa conexão WebSocket"""
        with client.websocket_connect("/ws/query") as websocket:
            # Deve receber mensagem de conexão
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert "message" in data
    
    def test_websocket_without_question(self):
        """Testa WebSocket sem enviar pergunta"""
        with client.websocket_connect("/ws/query") as websocket:
            # Recebe connected
            websocket.receive_json()
            
            # Envia mensagem vazia
            websocket.send_json({})
            
            # Deve receber erro
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert "Pergunta não fornecida" in data["message"]
    
    def test_websocket_with_question(self):
        """Testa WebSocket com pergunta"""
        with client.websocket_connect("/ws/query") as websocket:
            # Recebe connected
            connected = websocket.receive_json()
            assert connected["type"] == "connected"
            
            # Envia pergunta
            websocket.send_json({"question": "Quantas tabelas existem?"})
            
            # Deve receber eventos
            events = []
            messages = []
            max_events = 15  # Máximo de eventos esperados
            
            for _ in range(max_events):
                try:
                    data = websocket.receive_json()
                    events.append(data["type"])
                    messages.append(data)
                    
                    # Se recebeu end ou error, para
                    if data["type"] in ["end", "error"]:
                        break
                except Exception as e:
                    # Timeout ou desconexão
                    break
            
            # Deve ter recebido pelo menos alguns eventos
            # Como pode não haver tabelas no banco, esperamos erro ou fluxo completo
            assert len(events) > 0, f"Nenhum evento recebido. Mensagens: {messages}"
            assert "end" in events or "error" in events, f"Eventos: {events}"


class TestDocumentation:
    """Testes para documentação automática"""
    
    def test_openapi_docs(self):
        """Testa acesso à documentação OpenAPI"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_docs(self):
        """Testa acesso à documentação ReDoc"""
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_json(self):
        """Testa schema OpenAPI JSON"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Interview AI - Datasheet Importer"


class TestCORS:
    """Testes para configuração CORS"""
    
    def test_cors_headers(self):
        """Testa se headers CORS estão presentes"""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        # FastAPI adiciona headers CORS automaticamente
        assert "access-control-allow-origin" in response.headers or \
               "Access-Control-Allow-Origin" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
