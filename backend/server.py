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
    Quote, QuoteCreate,
    Authorization, AuthorizationCreate,
    Alert, AlertCreate,
    FileRecord,
    AssetReplacement, AssetReplacementCreate,
    DashboardStats
)
from auth import get_password_hash, verify_password, create_access_token, decode_token, security
from services.notification_service import send_alert_notification
from services.sql_service import sql_service
from services.analytics_service import AnalyticsService

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
    user: User = Depends(get_current_user)
):
    """Aprobar autorización (solo admin/gerente)"""
    if user.role not in ["admin", "gerente"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para aprobar autorizaciones")
    
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
    
    return {"message": "Autorización aprobada"}

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
