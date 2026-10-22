from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import uuid
import shutil

from models import (
    User, UserCreate, UserLogin, Token,
    Asset, AssetCreate,
    Maintenance, MaintenanceCreate,
    MaintenancePlan, MaintenancePlanCreate,
    Quote, QuoteCreate,
    Authorization, AuthorizationCreate,
    Alert, AlertCreate,
    FileRecord,
    AssetReplacement, AssetReplacementCreate,
    DashboardStats
)
from models_config import Config, ConfigCreate, ConfigUpdate, ConfigPublic, TestNotificationRequest
from auth import get_password_hash, verify_password, create_access_token, decode_token, security
from services.notification_service import NotificationService
from services.sql_service import sql_service
from services.analytics_service import AnalyticsService
from services.config_service import ConfigService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create uploads directory
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Create the main app
app = FastAPI(title="AssetGuard Pro API")
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Analytics service
analytics = AnalyticsService(db)

# Config service
config_service = ConfigService(db)

# Notification service
notification_service = NotificationService(config_service)

# Initialize config service on startup
@app.on_event("startup")
async def startup_event():
    await config_service.load_cache()
    logger.info("Config service initialized")

# Auth dependency
async def get_current_user(credentials = Depends(security)) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    user_data = await db.users.find_one({"id": user_id}, {"_id": 0})
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    if isinstance(user_data.get('created_at'), str):
        user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
    
    return User(**user_data)

# ============ AUTH ROUTES ============

@api_router.post("/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Registrar nuevo usuario"""
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.model_dump()
    del user_dict["password"]
    
    user = User(**user_dict)
    doc = user.model_dump()
    doc["hashed_password"] = hashed_password
    doc["created_at"] = doc["created_at"].isoformat()
    
    await db.users.insert_one(doc)
    return user

@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Iniciar sesión"""
    user_data = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user_data:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    if not verify_password(credentials.password, user_data.get("hashed_password", "")):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    if not user_data.get("active", True):
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    
    if isinstance(user_data.get('created_at'), str):
        user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
    
    user = User(**user_data)
    access_token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role})
    
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.post("/auth/reset-password-request")
async def reset_password_request(email: str):
    """Solicitar cambio de contraseña - genera código temporal"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        # Por seguridad, no revelamos si el email existe o no
        return {"message": "Si el email existe, recibirás instrucciones para restablecer tu contraseña"}
    
    # Generar código temporal de 6 dígitos
    import random
    reset_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Guardar código en la BD con expiración de 15 minutos
    from datetime import timedelta
    expiration = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    await db.users.update_one(
        {"email": email},
        {
            "$set": {
                "reset_code": reset_code,
                "reset_code_expiration": expiration.isoformat()
            }
        }
    )
    
    # En producción, enviaríamos el código por email
    # Por ahora, lo devolvemos en la respuesta para testing
    logger.info(f"Código de reseteo para {email}: {reset_code}")
    
    return {
        "message": "Código de reseteo generado",
        "reset_code": reset_code,
        "expires_in_minutes": 15,
        "note": "En producción, este código se enviaría por email"
    }

@api_router.post("/auth/reset-password-confirm")
async def reset_password_confirm(email: str, reset_code: str, new_password: str):
    """Confirmar cambio de contraseña con código"""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar código
    if not user.get("reset_code") or user.get("reset_code") != reset_code:
        raise HTTPException(status_code=400, detail="Código inválido")
    
    # Verificar expiración
    if user.get("reset_code_expiration"):
        expiration = datetime.fromisoformat(user["reset_code_expiration"])
        if datetime.now(timezone.utc) > expiration:
            raise HTTPException(status_code=400, detail="Código expirado")
    
    # Cambiar contraseña
    hashed_password = get_password_hash(new_password)
    await db.users.update_one(
        {"email": email},
        {
            "$set": {"hashed_password": hashed_password},
            "$unset": {"reset_code": "", "reset_code_expiration": ""}
        }
    )
    
    logger.info(f"Contraseña reseteada para {email}")
    
    return {"message": "Contraseña actualizada exitosamente"}

@api_router.post("/auth/admin-reset-password")
async def admin_reset_password(
    target_email: str,
    new_password: str,
    user: User = Depends(get_current_user)
):
    """Resetear contraseña de otro usuario (solo admin)"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden resetear contraseñas")
    
    target_user = await db.users.find_one({"email": target_email}, {"_id": 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    hashed_password = get_password_hash(new_password)
    await db.users.update_one(
        {"email": target_email},
        {"$set": {"hashed_password": hashed_password}}
    )
    
    logger.info(f"Admin {user.email} reseteó contraseña de {target_email}")
    
    return {"message": f"Contraseña de {target_email} actualizada exitosamente"}

@api_router.get("/auth/me", response_model=User)
async def get_me(user: User = Depends(get_current_user)):
    """Obtener usuario actual"""
    return user

# ============ ASSET ROUTES ============

@api_router.post("/assets", response_model=Asset, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate,
    user: User = Depends(get_current_user)
):
    """Crear nuevo activo"""
    # Verificar duplicados
    existing = await db.assets.find_one({"serial_number": asset_data.serial_number}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un activo con este número de serie")
    
    asset = Asset(**asset_data.model_dump(), created_by=user.id)
    doc = asset.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()
    
    await db.assets.insert_one(doc)
    return asset

@api_router.get("/assets", response_model=List[Asset])
async def get_assets(
    sucursal: Optional[str] = None,
    estado: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """Obtener lista de activos"""
    query = {}
    if sucursal:
        query["sucursal"] = sucursal
    if estado:
        query["estado"] = estado
    
    assets = await db.assets.find(query, {"_id": 0}).to_list(1000)
    for asset in assets:
        if isinstance(asset.get('created_at'), str):
            asset['created_at'] = datetime.fromisoformat(asset['created_at'])
    
    return assets

@api_router.get("/assets/{asset_id}", response_model=Asset)
async def get_asset(
    asset_id: str,
    user: User = Depends(get_current_user)
):
    """Obtener detalle de un activo"""
    asset = await db.assets.find_one({"id": asset_id}, {"_id": 0})
    if not asset:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    
    if isinstance(asset.get('created_at'), str):
        asset['created_at'] = datetime.fromisoformat(asset['created_at'])
    
    return Asset(**asset)

@api_router.put("/assets/{asset_id}", response_model=Asset)
async def update_asset(
    asset_id: str,
    asset_data: AssetCreate,
    user: User = Depends(get_current_user)
):
    """Actualizar activo"""
    existing = await db.assets.find_one({"id": asset_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    
    update_data = asset_data.model_dump()
    await db.assets.update_one({"id": asset_id}, {"$set": update_data})
    
    updated_asset = await db.assets.find_one({"id": asset_id}, {"_id": 0})
    if isinstance(updated_asset.get('created_at'), str):
        updated_asset['created_at'] = datetime.fromisoformat(updated_asset['created_at'])
    
    return Asset(**updated_asset)

# ============ MAINTENANCE ROUTES ============

@api_router.post("/maintenances", response_model=Maintenance, status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    maintenance_data: MaintenanceCreate,
    user: User = Depends(get_current_user)
):
    """Crear nuevo mantenimiento"""
    # Verificar que el activo existe
    asset = await db.assets.find_one({"id": maintenance_data.asset_id}, {"_id": 0})
    if not asset:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    
    maintenance = Maintenance(**maintenance_data.model_dump(), created_by=user.id)
    doc = maintenance.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()
    
    await db.maintenances.insert_one(doc)
    
    # Actualizar estado del activo si es necesario
    if maintenance_data.estado == "en_proceso":
        await db.assets.update_one(
            {"id": maintenance_data.asset_id},
            {"$set": {"estado": "mantenimiento"}}
        )
    
    return maintenance

@api_router.get("/maintenances", response_model=List[Maintenance])
async def get_maintenances(
    asset_id: Optional[str] = None,
    estado: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """Obtener lista de mantenimientos"""
    query = {}
    if asset_id:
        query["asset_id"] = asset_id
    if estado:
        query["estado"] = estado
    
    maintenances = await db.maintenances.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for maintenance in maintenances:
        if isinstance(maintenance.get('created_at'), str):
            maintenance['created_at'] = datetime.fromisoformat(maintenance['created_at'])
    
    return maintenances

@api_router.put("/maintenances/{maintenance_id}", response_model=Maintenance)
async def update_maintenance(
    maintenance_id: str,
    maintenance_data: MaintenanceCreate,
    user: User = Depends(get_current_user)
):
    """Actualizar mantenimiento"""
    existing = await db.maintenances.find_one({"id": maintenance_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
    
    update_data = maintenance_data.model_dump()
    await db.maintenances.update_one({"id": maintenance_id}, {"$set": update_data})
    
    # Si se completó, actualizar costos del activo
    if maintenance_data.estado == "completado":
        costs = await analytics.calculate_asset_total_cost(maintenance_data.asset_id)
        await db.assets.update_one(
            {"id": maintenance_data.asset_id},
            {
                "$set": {
                    "total_gasto_mantenimiento": costs["total_mantenimiento_preventivo"],
                    "total_gasto_reparaciones": costs["total_reparaciones"],
                    "estado": "operativo",
                    "ultimo_mantenimiento": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Verificar si se debe recomendar reemplazo
        replacement_check = await analytics.should_replace_asset(maintenance_data.asset_id)
        if replacement_check["should_replace"]:
            alert = Alert(
                asset_id=maintenance_data.asset_id,
                tipo="reemplazo_sugerido",
                titulo="Reemplazo de Equipo Sugerido",
                mensaje=f"El equipo ha superado el 70% de su valor en reparaciones. {replacement_check['reason']}",
                prioridad="alta"
            )
            alert_doc = alert.model_dump()
            alert_doc["created_at"] = alert_doc["created_at"].isoformat()
            await db.alerts.insert_one(alert_doc)
    
    updated = await db.maintenances.find_one({"id": maintenance_id}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    
    return Maintenance(**updated)


# ============ MAINTENANCE PLAN ROUTES ============

@api_router.post("/maintenance-plans", response_model=MaintenancePlan, status_code=status.HTTP_201_CREATED)
async def create_maintenance_plan(
    plan_data: MaintenancePlanCreate,
    user: User = Depends(get_current_user)
):
    """Crear nuevo plan de mantenimiento preventivo"""
    plan = MaintenancePlan(**plan_data.model_dump(), created_by=user.id)
    doc = plan.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()
    
    await db.maintenance_plans.insert_one(doc)
    return plan

@api_router.get("/maintenance-plans", response_model=List[MaintenancePlan])
async def get_maintenance_plans(
    activo: Optional[bool] = None,
    user: User = Depends(get_current_user)
):
    """Obtener planes de mantenimiento"""
    query = {}
    if activo is not None:
        query["activo"] = activo
    
    plans = await db.maintenance_plans.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for plan in plans:
        if isinstance(plan.get('created_at'), str):
            plan['created_at'] = datetime.fromisoformat(plan['created_at'])
    
    return plans

@api_router.get("/maintenance-plans/{plan_id}", response_model=MaintenancePlan)
async def get_maintenance_plan(
    plan_id: str,
    user: User = Depends(get_current_user)
):
    """Obtener detalle de un plan"""
    plan = await db.maintenance_plans.find_one({"id": plan_id}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    if isinstance(plan.get('created_at'), str):
        plan['created_at'] = datetime.fromisoformat(plan['created_at'])
    
    return MaintenancePlan(**plan)

@api_router.put("/maintenance-plans/{plan_id}", response_model=MaintenancePlan)
async def update_maintenance_plan(
    plan_id: str,
    plan_data: MaintenancePlanCreate,
    user: User = Depends(get_current_user)
):
    """Actualizar plan de mantenimiento"""
    existing = await db.maintenance_plans.find_one({"id": plan_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    update_data = plan_data.model_dump()
    await db.maintenance_plans.update_one({"id": plan_id}, {"$set": update_data})
    
    updated = await db.maintenance_plans.find_one({"id": plan_id}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    
    return MaintenancePlan(**updated)

@api_router.delete("/maintenance-plans/{plan_id}")
async def delete_maintenance_plan(
    plan_id: str,
    user: User = Depends(get_current_user)
):
    """Eliminar plan de mantenimiento"""
    if user.role not in ["admin", "gerente"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar planes")
    
    result = await db.maintenance_plans.delete_one({"id": plan_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    return {"message": "Plan eliminado exitosamente"}

@api_router.get("/quotes/check-requirement/{asset_id}")
async def check_quote_requirement(
    asset_id: str,
    monto: float,
    user: User = Depends(get_current_user)
):
    """Verificar si se requieren 2 cotizaciones para el monto dado"""
    # Get threshold from config
    threshold_str = await config_service.get("QUOTE_THRESHOLD", "5000")
    threshold = float(threshold_str)
    
    requires_multiple = monto >= threshold
    
    if not requires_multiple:
        return {
            "requires_multiple_quotes": False,
            "threshold": threshold,
            "message": "No se requieren múltiples cotizaciones"
        }
    
    # Check how many quotes exist for this asset
    existing_quotes = await db.quotes.count_documents({
        "asset_id": asset_id,
        "estado": {"$in": ["pendiente", "aprobada"]}
    })
    
    return {
        "requires_multiple_quotes": True,
        "threshold": threshold,
        "existing_quotes": existing_quotes,
        "min_required": 2,
        "can_proceed": existing_quotes >= 1,
        "message": f"Se requieren mínimo 2 cotizaciones. Actualmente hay {existing_quotes}."
    }

@api_router.put("/maintenance-plans/{plan_id}", response_model=MaintenancePlan)
async def update_maintenance_plan(
    plan_id: str,
    plan_data: MaintenancePlanCreate,
    user: User = Depends(get_current_user)
):
    """Actualizar plan de mantenimiento"""
    existing = await db.maintenance_plans.find_one({"id": plan_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    update_data = plan_data.model_dump()
    await db.maintenance_plans.update_one({"id": plan_id}, {"$set": update_data})
    
    updated = await db.maintenance_plans.find_one({"id": plan_id}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    
    return MaintenancePlan(**updated)

@api_router.delete("/maintenance-plans/{plan_id}")
async def delete_maintenance_plan(
    plan_id: str,
    user: User = Depends(get_current_user)
):
    """Eliminar plan de mantenimiento"""
    if user.role not in ["admin", "gerente"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar planes")
    
    result = await db.maintenance_plans.delete_one({"id": plan_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    return {"message": "Plan eliminado exitosamente"}

# ============ QUOTE ROUTES ============

@api_router.post("/quotes", response_model=Quote, status_code=status.HTTP_201_CREATED)
async def create_quote(
    quote_data: QuoteCreate,
    user: User = Depends(get_current_user)
):
    """Crear nueva cotización"""
    quote = Quote(**quote_data.model_dump(), created_by=user.id)
    doc = quote.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()
    
    await db.quotes.insert_one(doc)
    return quote

@api_router.get("/quotes", response_model=List[Quote])
async def get_quotes(
    asset_id: Optional[str] = None,
    maintenance_id: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """Obtener cotizaciones"""
    query = {}
    if asset_id:
        query["asset_id"] = asset_id
    if maintenance_id:
        query["maintenance_id"] = maintenance_id
    
    quotes = await db.quotes.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for quote in quotes:
        if isinstance(quote.get('created_at'), str):
            quote['created_at'] = datetime.fromisoformat(quote['created_at'])
    
    return quotes

# ============ AUTHORIZATION ROUTES ============

@api_router.post("/authorizations", response_model=Authorization, status_code=status.HTTP_201_CREATED)
async def create_authorization(
    auth_data: AuthorizationCreate,
    user: User = Depends(get_current_user)
):
    """Solicitar autorización"""
    authorization = Authorization(**auth_data.model_dump())
    doc = authorization.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()
    
    await db.authorizations.insert_one(doc)
    
    # Crear alerta
    alert = Alert(
        asset_id=auth_data.referencia_id,
        tipo="autorizacion_pendiente",
        titulo="Nueva Autorización Pendiente",
        mensaje=f"Se ha solicitado autorización para {auth_data.tipo}. Monto: ${auth_data.monto or 0}",
        prioridad="media"
    )
    alert_doc = alert.model_dump()
    alert_doc["created_at"] = alert_doc["created_at"].isoformat()
    await db.alerts.insert_one(alert_doc)
    
    return authorization

@api_router.get("/authorizations", response_model=List[Authorization])
async def get_authorizations(
    estado: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """Obtener autorizaciones"""
    query = {}
    if estado:
        query["estado"] = estado
    
    authorizations = await db.authorizations.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for auth in authorizations:
        if isinstance(auth.get('created_at'), str):
            auth['created_at'] = datetime.fromisoformat(auth['created_at'])
    
    return authorizations

@api_router.put("/authorizations/{authorization_id}/approve")
async def approve_authorization(
    authorization_id: str,
    comentarios: Optional[str] = None,
    notificar_whatsapp: bool = False,
    user: User = Depends(get_current_user)
):
    """Aprobar autorización (solo admin/gerente)"""
    if user.role not in ["admin", "gerente"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para aprobar autorizaciones")
    
    # Get authorization details
    authorization = await db.authorizations.find_one({"id": authorization_id}, {"_id": 0})
    if not authorization:
        raise HTTPException(status_code=404, detail="Autorización no encontrada")
    
    await db.authorizations.update_one(
        {"id": authorization_id},
        {
            "$set": {
                "estado": "aprobada",
                "aprobador_id": user.id,
                "fecha_resolucion": datetime.now(timezone.utc).isoformat(),
                "comentarios": comentarios
            }
        }
    )
    
    # Send WhatsApp notification if requested
    if notificar_whatsapp:
        # Get solicitante details
        solicitante = await db.users.find_one({"id": authorization.get("solicitante_id")}, {"_id": 0})
        if solicitante and solicitante.get("phone"):
            alert_data = {
                "titulo": "Autorización Aprobada",
                "mensaje": f"Tu solicitud de {authorization.get('tipo')} ha sido aprobada por {user.full_name}. {comentarios or ''}",
                "prioridad": "media"
            }
            await notification_service.send_alert_notification(
                "authorization_approved",
                solicitante.get("email"),
                solicitante.get("phone"),
                alert_data
            )
    
    return {"message": "Autorización aprobada", "notification_sent": notificar_whatsapp}

@api_router.put("/authorizations/{authorization_id}/reject")
async def reject_authorization(
    authorization_id: str,
    comentarios: str,
    notificar_whatsapp: bool = False,
    user: User = Depends(get_current_user)
):
    """Rechazar autorización (solo admin/gerente)"""
    if user.role not in ["admin", "gerente"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para rechazar autorizaciones")
    
    # Get authorization details
    authorization = await db.authorizations.find_one({"id": authorization_id}, {"_id": 0})
    if not authorization:
        raise HTTPException(status_code=404, detail="Autorización no encontrada")
    
    await db.authorizations.update_one(
        {"id": authorization_id},
        {
            "$set": {
                "estado": "rechazada",
                "aprobador_id": user.id,
                "fecha_resolucion": datetime.now(timezone.utc).isoformat(),
                "comentarios": comentarios
            }
        }
    )
    
    # Send WhatsApp notification if requested
    if notificar_whatsapp:
        # Get solicitante details
        solicitante = await db.users.find_one({"id": authorization.get("solicitante_id")}, {"_id": 0})
        if solicitante and solicitante.get("phone"):
            alert_data = {
                "titulo": "Autorización Rechazada",
                "mensaje": f"Tu solicitud de {authorization.get('tipo')} ha sido rechazada por {user.full_name}. Motivo: {comentarios}",
                "prioridad": "alta"
            }
            await notification_service.send_alert_notification(
                "authorization_rejected",
                solicitante.get("email"),
                solicitante.get("phone"),
                alert_data
            )
    
    return {"message": "Autorización rechazada", "notification_sent": notificar_whatsapp}


# ============ CONFIGURATION ROUTES (Admin Only) ============

@api_router.get("/config", response_model=List[ConfigPublic])
async def get_all_configs(user: User = Depends(get_current_user)):
    """Obtener todas las configuraciones (solo admin)"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden acceder a las configuraciones")
    
    configs = await db.configs.find({}, {"_id": 0}).to_list(1000)
    
    # Mask sensitive values
    result = []
    for config in configs:
        if isinstance(config.get('created_at'), str):
            config['created_at'] = datetime.fromisoformat(config['created_at'])
        if isinstance(config.get('updated_at'), str):
            config['updated_at'] = datetime.fromisoformat(config['updated_at'])
        
        config_dict = Config(**config).model_dump()
        
        # Mask sensitive values
        if config_dict.get('is_sensitive') and config_dict.get('value'):
            masked_value = config_dict['value'][:4] + "*" * (len(config_dict['value']) - 4) if len(config_dict['value']) > 4 else "****"
            config_dict['value'] = masked_value
        
        result.append(ConfigPublic(**config_dict))
    
    return result

@api_router.get("/config/{config_id}", response_model=Config)
async def get_config(config_id: str, user: User = Depends(get_current_user)):
    """Obtener configuración específica (solo admin)"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden acceder a las configuraciones")
    
    config = await db.configs.find_one({"id": config_id}, {"_id": 0})
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    
    if isinstance(config.get('created_at'), str):
        config['created_at'] = datetime.fromisoformat(config['created_at'])
    if isinstance(config.get('updated_at'), str):
        config['updated_at'] = datetime.fromisoformat(config['updated_at'])
    
    return Config(**config)

@api_router.put("/config/{config_id}")
async def update_config(
    config_id: str,
    update_data: ConfigUpdate,
    user: User = Depends(get_current_user)
):
    """Actualizar configuración (solo admin)"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden modificar configuraciones")
    
    config = await db.configs.find_one({"id": config_id}, {"_id": 0})
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    
    update_dict = {}
    if update_data.value is not None:
        update_dict["value"] = update_data.value
    if update_data.description is not None:
        update_dict["description"] = update_data.description
    if update_data.active is not None:
        update_dict["active"] = update_data.active
    
    if update_dict:
        update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
        update_dict["updated_by"] = user.id
        
        await db.configs.update_one({"id": config_id}, {"$set": update_dict})
        
        # Reload config cache
        await config_service.reload_cache()
        logger.info(f"Config {config['key']} updated by {user.email}")
    
    return {"message": "Configuración actualizada exitosamente"}

@api_router.post("/config/test-notification")
async def test_notification(
    request: TestNotificationRequest,
    user: User = Depends(get_current_user)
):
    """Enviar notificación de prueba (solo admin)"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden probar notificaciones")
    
    alert_data = {
        "titulo": "Prueba de Notificación",
        "mensaje": "Este es un mensaje de prueba del sistema AssetGuard Pro",
        "prioridad": "media"
    }
    
    results = await notification_service.send_alert_notification(
        "test",
        request.test_email,
        request.test_phone,
        alert_data
    )
    
    return {
        "message": "Notificación de prueba enviada",
        "results": results
    }

# ============ ALERT ROUTES ============

@api_router.get("/alerts", response_model=List[Alert])
async def get_alerts(
    leida: Optional[bool] = None,
    user: User = Depends(get_current_user)
):
    """Obtener alertas"""
    query = {}
    if leida is not None:
        query["leida"] = leida
    
    alerts = await db.alerts.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    for alert in alerts:
        if isinstance(alert.get('created_at'), str):
            alert['created_at'] = datetime.fromisoformat(alert['created_at'])
    
    return alerts

@api_router.put("/alerts/{alert_id}/mark-read")
async def mark_alert_read(
    alert_id: str,
    user: User = Depends(get_current_user)
):
    """Marcar alerta como leída"""
    await db.alerts.update_one({"id": alert_id}, {"$set": {"leida": True}})
    return {"message": "Alerta marcada como leída"}

# ============ FILE UPLOAD ROUTES ============

@api_router.post("/upload", response_model=FileRecord)
async def upload_file(
    file: UploadFile = File(...),
    entity_type: str = Form(...),
    entity_id: str = Form(...),
    user: User = Depends(get_current_user)
):
    """Subir archivo (PDF, XML, imagen)"""
    # Validar tipo de archivo
    allowed_types = ["application/pdf", "application/xml", "text/xml", "image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")
    
    # Generar nombre único
    file_ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Guardar archivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Crear registro
    file_record = FileRecord(
        filename=unique_filename,
        original_name=file.filename,
        file_type=file.content_type,
        entity_type=entity_type,
        entity_id=entity_id,
        uploaded_by=user.id,
        file_path=str(file_path)
    )
    
    doc = file_record.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()
    await db.files.insert_one(doc)
    
    return file_record

@api_router.get("/files/{entity_type}/{entity_id}", response_model=List[FileRecord])
async def get_files(
    entity_type: str,
    entity_id: str,
    user: User = Depends(get_current_user)
):
    """Obtener archivos de una entidad"""
    files = await db.files.find(
        {"entity_type": entity_type, "entity_id": entity_id},
        {"_id": 0}
    ).to_list(100)
    
    for file in files:
        if isinstance(file.get('created_at'), str):
            file['created_at'] = datetime.fromisoformat(file['created_at'])
    
    return files

@api_router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    user: User = Depends(get_current_user)
):
    """Descargar archivo"""
    file_record = await db.files.find_one({"id": file_id}, {"_id": 0})
    if not file_record:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    file_path = Path(file_record["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el sistema")
    
    return FileResponse(
        path=file_path,
        filename=file_record["original_name"],
        media_type=file_record["file_type"]
    )

# ============ ANALYTICS ROUTES ============

@api_router.get("/analytics/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    user: User = Depends(get_current_user)
):
    """Obtener estadísticas del dashboard"""
    stats = await analytics.get_dashboard_stats()
    return DashboardStats(**stats)

@api_router.get("/analytics/asset/{asset_id}/costs")
async def get_asset_costs(
    asset_id: str,
    user: User = Depends(get_current_user)
):
    """Obtener costos de un activo"""
    costs = await analytics.calculate_asset_total_cost(asset_id)
    return costs

@api_router.get("/analytics/asset/{asset_id}/replacement-check")
async def check_asset_replacement(
    asset_id: str,
    user: User = Depends(get_current_user)
):
    """Verificar si un activo debe ser reemplazado"""
    check = await analytics.should_replace_asset(asset_id)
    return check


# ============ REPORTS ROUTES ============

@api_router.get("/reports/maintenance-history")
async def get_maintenance_history(
    asset_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tipo: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """Obtener historial de mantenimientos y reparaciones"""
    query = {"estado": "completado"}
    
    if asset_id:
        query["asset_id"] = asset_id
    if tipo:
        query["tipo"] = tipo
    if start_date:
        query["fecha_realizada"] = {"$gte": start_date}
    if end_date:
        if "fecha_realizada" in query:
            query["fecha_realizada"]["$lte"] = end_date
        else:
            query["fecha_realizada"] = {"$lte": end_date}
    
    maintenances = await db.maintenances.find(query, {"_id": 0}).sort("fecha_realizada", -1).to_list(1000)
    
    # Enrich with asset details
    if maintenances:
        asset_ids = list({m.get("asset_id") for m in maintenances if m.get("asset_id")})
        assets_res = await db.assets.find({"id": {"$in": asset_ids}}, {"_id": 0}).to_list(None)
        asset_map = {asset["id"]: asset for asset in assets_res if "id" in asset}
        
        for maintenance in maintenances:
            if isinstance(maintenance.get('created_at'), str):
                maintenance['created_at'] = datetime.fromisoformat(maintenance['created_at'])

            asset = asset_map.get(maintenance.get("asset_id"))
            if asset:
                maintenance["asset_details"] = {
                    "etiqueta_id": asset.get("etiqueta_id"),
                    "marca": asset.get("marca"),
                    "modelo": asset.get("modelo"),
                    "sucursal": asset.get("sucursal"),
                    "area_restaurante": asset.get("area_restaurante")
                }
    
    return {
        "total": len(maintenances),
        "maintenances": maintenances
    }

@api_router.get("/reports/asset-summary/{asset_id}")
async def get_asset_summary(
    asset_id: str,
    user: User = Depends(get_current_user)
):
    """Obtener resumen completo de un activo"""
    asset = await db.assets.find_one({"id": asset_id}, {"_id": 0})
    if not asset:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    
    if isinstance(asset.get('created_at'), str):
        asset['created_at'] = datetime.fromisoformat(asset['created_at'])
    
    # Get maintenance history
    maintenances = await db.maintenances.find(
        {"asset_id": asset_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    for m in maintenances:
        if isinstance(m.get('created_at'), str):
            m['created_at'] = datetime.fromisoformat(m['created_at'])
    
    # Get costs
    costs = await analytics.calculate_asset_total_cost(asset_id)
    
    # Get replacement check
    replacement = await analytics.should_replace_asset(asset_id)
    
    # Get quotes
    quotes = await db.quotes.find({"asset_id": asset_id}, {"_id": 0}).to_list(100)
    for q in quotes:
        if isinstance(q.get('created_at'), str):
            q['created_at'] = datetime.fromisoformat(q['created_at'])
    
    return {
        "asset": asset,
        "maintenances": maintenances,
        "costs": costs,
        "replacement_recommendation": replacement,
        "quotes": quotes
    }

# ============ SQL SERVER ROUTES ============

@api_router.get("/external/invoices/{server_index}")
async def get_external_invoices(
    server_index: int,
    user: User = Depends(get_current_user)
):
    """Obtener facturas de servidores externos SQL"""
    if server_index not in [0, 1, 2]:
        raise HTTPException(status_code=400, detail="Índice de servidor inválido (0-2)")
    
    invoices = await sql_service.get_invoices(server_index)
    return {"server_index": server_index, "invoices": invoices}

@api_router.get("/external/search-invoice/{invoice_number}")
async def search_external_invoice(
    invoice_number: str,
    user: User = Depends(get_current_user)
):
    """Buscar factura en todos los servidores externos"""
    results = await sql_service.search_by_invoice_number(invoice_number)
    return {"invoice_number": invoice_number, "results": results}

# ============ ASSET REPLACEMENT ROUTES ============

@api_router.post("/asset-replacements", response_model=AssetReplacement, status_code=status.HTTP_201_CREATED)
async def create_asset_replacement(
    replacement_data: AssetReplacementCreate,
    user: User = Depends(get_current_user)
):
    """Registrar proceso de baja y sustitución de activo"""
    # Verificar que ambos activos existen
    old_asset = await db.assets.find_one({"id": replacement_data.old_asset_id}, {"_id": 0})
    new_asset = await db.assets.find_one({"id": replacement_data.new_asset_id}, {"_id": 0})
    
    if not old_asset or not new_asset:
        raise HTTPException(status_code=404, detail="Uno de los activos no fue encontrado")
    
    replacement = AssetReplacement(**replacement_data.model_dump(), created_by=user.id)
    doc = replacement.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()
    
    await db.asset_replacements.insert_one(doc)
    
    # Actualizar estado del activo viejo
    await db.assets.update_one(
        {"id": replacement_data.old_asset_id},
        {"$set": {"estado": "dado_de_baja"}}
    )
    
    return replacement

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
