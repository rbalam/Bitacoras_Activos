from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def calculate_asset_total_cost(self, asset_id: str) -> Dict[str, float]:
        """Calcular costos totales de un activo"""
        maintenances = await self.db.maintenances.find(
            {"asset_id": asset_id, "estado": "completado"},
            {"_id": 0, "tipo": 1, "costo": 1}
        ).to_list(1000)
        
        total_preventivo = sum(m["costo"] for m in maintenances if m.get("tipo") == "preventivo")
        total_correctivo = sum(m["costo"] for m in maintenances if m.get("tipo") in ["correctivo", "emergencia"])
        total_general = total_preventivo + total_correctivo
        
        return {
            "total_mantenimiento_preventivo": total_preventivo,
            "total_reparaciones": total_correctivo,
            "total_general": total_general
        }
    
    async def should_replace_asset(self, asset_id: str) -> Dict[str, Any]:
        """Determinar si un activo debe ser reemplazado"""
        asset = await self.db.assets.find_one({"id": asset_id}, {"_id": 0})
        if not asset:
            return {"should_replace": False, "reason": "Activo no encontrado"}
        
        costs = await self.calculate_asset_total_cost(asset_id)
        costo_equipo = asset.get("costo_equipo", 0)
        
        # Solo considerar reparaciones (excluir preventivo)
        costo_reparaciones = costs["total_reparaciones"]
        
        # Criterio: Si las reparaciones superan el 70% del costo del equipo
        threshold = costo_equipo * 0.7
        should_replace = costo_reparaciones >= threshold
        
        percentage = (costo_reparaciones / costo_equipo * 100) if costo_equipo > 0 else 0
        
        return {
            "should_replace": should_replace,
            "costo_equipo": costo_equipo,
            "costo_reparaciones": costo_reparaciones,
            "porcentaje": round(percentage, 2),
            "threshold": threshold,
            "reason": f"Las reparaciones representan el {percentage:.1f}% del costo del equipo" if should_replace else "El equipo aún es viable económicamente"
        }
    
    async def get_monthly_costs(self, year: int, month: int) -> float:
        """Obtener costos totales del mes"""
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        maintenances = await self.db.maintenances.find(
            {
                "estado": "completado",
                "fecha_realizada": {"$gte": start_date, "$lt": end_date}
            },
            {"_id": 0, "costo": 1}
        ).to_list(1000)
        
        return sum(m.get("costo", 0) for m in maintenances)
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas para el dashboard"""
        total_assets = await self.db.assets.count_documents({})
        assets_operativos = await self.db.assets.count_documents({"estado": "operativo"})
        assets_mantenimiento = await self.db.assets.count_documents({"estado": "mantenimiento"})
        assets_criticos = await self.db.assets.count_documents({"estado": "critico"})
        
        mantenimientos_pendientes = await self.db.maintenances.count_documents(
            {"estado": {"$in": ["programado", "en_proceso"]}}
        )
        
        autorizaciones_pendientes = await self.db.authorizations.count_documents(
            {"estado": "pendiente"}
        )
        
        alertas_activas = await self.db.alerts.count_documents({"leida": False})
        
        now = datetime.now(timezone.utc)
        current_month = now.month
        current_year = now.year
        gasto_mes_actual = await self.get_monthly_costs(current_year, current_month)
        
        return {
            "total_assets": total_assets,
            "assets_operativos": assets_operativos,
            "assets_mantenimiento": assets_mantenimiento,
            "assets_criticos": assets_criticos,
            "mantenimientos_pendientes": mantenimientos_pendientes,
            "autorizaciones_pendientes": autorizaciones_pendientes,
            "alertas_activas": alertas_activas,
            "gasto_mes_actual": gasto_mes_actual
        }
