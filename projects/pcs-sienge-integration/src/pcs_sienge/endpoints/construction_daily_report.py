from __future__ import annotations

from datetime import date
from typing import Optional
from ..client import SiengeClient


def list_construction_daily_reports(
    client: SiengeClient,
    building_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """
    GET /construction-daily-report
    Lista os Diários de Obra paginados.

    Requer permissão: construction-daily-report (solicitar no admin Sienge)

    Args:
        building_id: Id da Obra (buildingId - ver /cost-centers para IDs)
        start_date: Data início no formato yyyy-MM-dd (ex: 2026-01-01)
        end_date: Data fim no formato yyyy-MM-dd (ex: 2026-04-19)
        limit: Máximo 200
        offset: Paginação
    """
    params = {"limit": limit, "offset": offset}
    if building_id is not None:
        params["buildingId"] = building_id
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    return client.get("construction-daily-report", params=params)


def get_construction_daily_report(
    client: SiengeClient,
    building_id: int,
    construction_daily_id: int,
):
    """
    GET /construction-daily-report/{buildingId}/{constructionDailyId}
    Retorna todos os dados de um Diário de Obra específico.

    Campos retornados: id, buildingId, date, responsibleId, rainfallIndex,
    weekDay, notes, createdBy, createdAt, modifiedBy, modifiedAt,
    shifts, plannedTasks, detachedTasks, events, crews, equipments, attachments
    """
    return client.get(f"construction-daily-report/{building_id}/{construction_daily_id}")


def create_construction_daily_report(
    client: SiengeClient,
    building_id: int,
    report_date: str,
    shifts: list,
    responsible_id: Optional[str] = None,
    notes: Optional[str] = None,
    rainfall_index: Optional[float] = None,
    planned_tasks: Optional[list] = None,
    detached_tasks: Optional[list] = None,
    events: Optional[list] = None,
    crews: Optional[list] = None,
    equipments: Optional[list] = None,
):
    """
    POST /construction-daily-report
    Cadastra um novo Diário de Obra.

    Args:
        building_id: Código da Obra (obrigatório)
        report_date: Data yyyy-MM-dd (obrigatório)
        shifts: Lista de turnos (obrigatório, mínimo 1)
            Cada turno: {description: Morning|Afternoon|Night,
                         startTime: HH:mm, finishTime: HH:mm,
                         weatherCondition: Fine|Light rain|Heavy rain|Unworkable}
        responsible_id: Código do responsável (ex: "ADMIN")
        notes: Observações (máx 4000 chars)
        rainfall_index: Índice pluviométrico (0 a 9999.99)
        planned_tasks: Tarefas do cronograma
            Cada tarefa: {buildingUnitId: int, taskId: int, quantity: float,
                          notes: str, supplierId: int, siteId: int}
        detached_tasks: Tarefas avulsas
            Cada tarefa: {description: str, quantity: float, unitOfMeasure: str,
                          notes: str, siteId: int}
        events: Ocorrências [{description: str, eventTypeId: int}]
        crews: Equipes [{resourceId: int, quantity: int, assignment: str,
                         crewTypeId: int}]
            assignment: DIRECT_LABOR | INDIRECT_LABOR | THIRD_PARTY
        equipments: Equipamentos [{resourceId: int, quantity: int, status: str,
                                   equipmentTypeId: int}]
            status: IN_USE | IDLE | OUT_OF_ORDER
    """
    body = {
        "buildingId": building_id,
        "date": report_date,
        "shifts": shifts,
    }
    if responsible_id:
        body["responsibleId"] = responsible_id
    if notes:
        body["notes"] = notes
    if rainfall_index is not None:
        body["rainfallIndex"] = rainfall_index
    if planned_tasks:
        body["plannedTasks"] = planned_tasks
    if detached_tasks:
        body["detachedTasks"] = detached_tasks
    if events:
        body["events"] = events
    if crews:
        body["crews"] = crews
    if equipments:
        body["equipments"] = equipments
    return client.post("construction-daily-report", body=body)


def get_event_types(client: SiengeClient, limit: int = 200, offset: int = 0):
    """
    GET /construction-daily-report/event-type
    Lista os tipos de ocorrência disponíveis.
    """
    return client.get("construction-daily-report/event-type",
                      params={"limit": limit, "offset": offset})


def get_all_types(
    client: SiengeClient,
    types: Optional[list] = None,
    limit: int = 200,
    offset: int = 0,
):
    """
    GET /construction-daily-report/types
    Lista os tipos de Ocorrência, Equipe e Equipamento.

    Args:
        types: Lista de tipos para filtrar. Valores: Event, Crew, Equipment
               Ex: ["Event", "Crew"] para retornar só ocorrências e equipes
    """
    params = {"limit": limit, "offset": offset}
    if types:
        params["types"] = types
    return client.get("construction-daily-report/types", params=params)
