import json
from datetime import datetime

from app.platform.persistence import platform_db
from app.domain.models.platform import Dataset


class DataExportSystem:
    """Export simulation data in multiple formats."""

    async def export(self, name: str, dataset_type: str, format: str = "json",
                     simulation_id: str = None, data: dict = None) -> dict:
        record_count = len(data) if isinstance(data, (list, dict)) and data else 0
        encoded = json.dumps(data or {})
        dataset = Dataset(
            name=name, dataset_type=dataset_type, format=format,
            simulation_id=simulation_id, data=encoded,
            record_count=record_count, size_bytes=len(encoded.encode("utf-8")),
        )
        saved = await platform_db.create_dataset(dataset)
        return {
            "id": saved.id, "name": saved.name, "format": saved.format,
            "type": saved.dataset_type, "records": record_count,
            "size_bytes": saved.size_bytes,
        }

    async def export_historical(self, simulation_id: str, events: list = None) -> dict:
        return await self.export(
            name=f"Historical Data - {simulation_id[:8]}",
            dataset_type="historical", format="json",
            simulation_id=simulation_id,
            data={"events": events or [], "exported_at": datetime.utcnow().isoformat()},
        )

    async def export_economic(self, simulation_id: str, indicators: list = None) -> dict:
        return await self.export(
            name=f"Economic Data - {simulation_id[:8]}",
            dataset_type="economic", format="csv",
            simulation_id=simulation_id,
            data={"indicators": indicators or [], "period": "quarterly"},
        )

    async def export_population(self, simulation_id: str, citizens: list = None) -> dict:
        return await self.export(
            name=f"Population Data - {simulation_id[:8]}",
            dataset_type="population", format="json",
            simulation_id=simulation_id,
            data={"citizens": citizens or [], "total": len(citizens or [])},
        )

    async def list_datasets(self, dataset_type: str = None) -> list[dict]:
        datasets = await platform_db.get_datasets(dataset_type)
        return [{
            "id": d.id, "name": d.name, "type": d.dataset_type, "format": d.format,
            "records": d.record_count, "size_bytes": d.size_bytes,
            "exported_at": d.exported_at.isoformat() if d.exported_at else None,
        } for d in datasets]


data_exporter = DataExportSystem()
