# MrNewton Analytics Provider

## Descrição

Backend do **MrNewton Analytics Provider** para a arquitetura **Inven!RA**. Este serviço fornece endpoints REST para analytics de atividades de Física, retornando métricas quantitativas e qualitativas sobre o desempenho dos estudantes.

## Tecnologias Utilizadas

- **Python 3.11+**
- **FastAPI** - Framework web moderno e rápido para APIs
- **Uvicorn** - Servidor ASGI de alto desempenho
- **Pydantic** - Validação de dados e serialização
- **Pytest** - Framework de testes

## Como Executar o Projeto (CMD/Windows)

### 1. Criar e ativar ambiente virtual

```cmd
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar dependências

```cmd
pip install -r requirements.txt
```

### 3. Executar o servidor

```cmd
python run.py
```

O servidor estará disponível em: **http://localhost:8000**

## Documentação

A documentação da API é gerada automaticamente pelo FastAPI e está disponível em:

- **Swagger UI (api-docs):** http://localhost:8000/api-docs
- **ReDoc:** http://localhost:8000/redoc

## Endpoints

### 1. GET /api-docs
Documentação interativa da API (Swagger UI). Permite visualizar e testar todos os endpoints disponíveis.

### 2. GET /api/v1/analytics/contract
Lista todos os analytics suportados pelo serviço, incluindo métricas qualitativas e quantitativas.

**Resposta:**
```json
{
  "qualitative": [
    {
      "name": "annotations",
      "type": "array",
      "description": "Anotações sobre o raciocínio do estudante"
    }
  ],
  "quantitative": [
    {"name": "started_exercises", "type": "integer"},
    {"name": "completed_exercises", "type": "integer"},
    {"name": "total_attempts", "type": "integer"},
    {"name": "total_time_seconds", "type": "integer"},
    {"name": "average_time_per_exercise", "type": "number"},
    {"name": "number_of_correct_answers", "type": "integer"},
    {"name": "final_score", "type": "number"},
    {"name": "activity_success", "type": "boolean"}
  ]
}
```

### 3. GET /api/v1/analytics/instances/{instance_id}/metrics
Retorna as métricas de analytics para uma instância específica de atividade, incluindo métricas quantitativas (tempo, tentativas, score) e anotações qualitativas sobre o desempenho do estudante.

**Parâmetros:**
- `instance_id` (path) - ID da instância da atividade

**Resposta:**
```json
{
  "instance_id": "inst_abc123",
  "invenra_user_id": "test-user-id",
  "metrics": {
    "started_exercises": 3,
    "completed_exercises": 3,
    "total_attempts": 2,
    "total_time_seconds": 4200,
    "average_time_per_exercise": 1400.0,
    "number_of_correct_answers": 2,
    "final_score": 0.67,
    "activity_success": true
  },
  "qualitative": {
    "annotations": [
      "A expressão da energia cinética foi escolhida de maneira apropriada...",
      "A 2.ª lei de Newton foi aplicada de forma adequada...",
      "A equação horária do movimento uniformemente acelerado foi usada corretamente..."
    ]
  },
  "calculated_at": "2025-11-23T12:00:00.000000Z"
}
```

---

**Versão:** 1.0.0  
**Status:** Protótipo
