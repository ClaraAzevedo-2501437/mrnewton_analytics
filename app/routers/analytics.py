from fastapi import APIRouter, Path
from datetime import datetime

router = APIRouter()


@router.get("/contract")
async def get_analytics_contract():
    """
    Get the analytics contract listing all supported qualitative and quantitative metrics.
    """
    return {
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


@router.get("/instances/{instance_id}/metrics")
async def get_instance_metrics(
    instance_id: str = Path(..., description="The instance ID to retrieve metrics for")
):
    """
    Get analytics metrics for a specific activity instance.
    Returns static example metrics.
    """
    return {
        "instance_id": instance_id,
        "invenra_user_id": "test-user-id",
        "metrics": {
            "started_exercises": 3,
            "completed_exercises": 3,
            "total_attempts": 2,
            "total_time_seconds": 4200,
            "average_time_per_exercise": 1400.0,
            "number_of_correct_answers": 2,
            "final_score": 0.67,
            "activity_success": True
        },
        "qualitative": {
            "annotations": [
                "A expressão da energia cinética foi escolhida de maneira apropriada, dado que a massa e a velocidade eram conhecidas e permitiam calcular diretamente a energia do movimento.",
                "A 2.ª lei de Newton foi aplicada de forma adequada, pois eram conhecidos a massa e o valor da aceleração, permitindo determinar a força resultante.",
                "A equação horária do movimento uniformemente acelerado foi usada corretamente, já que o problema indicava aceleração constante e era necessário calcular a distância."
            ]
        },
        "calculated_at": datetime.utcnow().isoformat() + "Z"
    }
