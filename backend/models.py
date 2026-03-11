from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime, timezone
import uuid

# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: Literal["admin", "tecnico", "gerente"]
    phone: Optional[str] = None
    active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Asset Models (Aire Acondicionado)
class AssetBase(BaseModel):
    serial_number: str
    etiqueta_id: str
    modelo: str
    marca: str
    capacidad: str
    area_restaurante: str
    sucursal: str
    ubicacion_especifica: Optional[str] = None
    costo_equipo: float
    fecha_compra: Optional[str] = None
    estado: Literal["operativo", "mantenimiento", "critico", "dado_de_baja"] = "operativo"
    foto_url: Optional[str] = None
    notas: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str
    total_gasto_mantenimiento: float = 0.0
    total_gasto_reparaciones: float = 0.0
    ultimo_mantenimiento: Optional[str] = None

# Maintenance Models
class MaintenanceBase(BaseModel):
    asset_id: str
    tipo: Literal["preventivo", "correctivo", "emergencia"]
    descripcion: str
    fecha_programada: Optional[str] = None
    fecha_realizada: Optional[str] = None
    tecnico_asignado: Optional[str] = None
    costo: float = 0.0
    estado: Literal["programado", "en_proceso", "completado", "cancelado"] = "programado"
    diagnostico: Optional[str] = None
    piezas_sustituidas: Optional[List[str]] = []
    fotos_evidencia: Optional[List[str]] = []
    factura_url: Optional[str] = None
    notas: Optional[str] = None

class MaintenanceCreate(MaintenanceBase):
    pass

class Maintenance(MaintenanceBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str

# Quote Models (Cotizaciones)
class QuoteBase(BaseModel):
    asset_id: str
    maintenance_id: Optional[str] = None
    tipo_cotizacion: Literal["mantenimiento", "refacciones"] = "mantenimiento"
    proveedor: str
    concepto: str
    monto: float
    validez_dias: int = 30
    incluye: Optional[str] = None
    archivo_url: Optional[str] = None
    estado: Literal["pendiente", "aprobada", "rechazada"] = "pendiente"
    # Relación con sistemas externos
    sistema_externo: Optional[Literal["mpro", "soft"]] = None
    pedido_externo_id: Optional[str] = None
    sucursal_sistema: Optional[str] = None
    notas: Optional[str] = None

class QuoteCreate(QuoteBase):
    pass

class Quote(QuoteBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str

# Authorization Models
class AuthorizationBase(BaseModel):
    tipo: Literal["mantenimiento", "compra", "baja_equipo", "sustitucion"]
    referencia_id: str
    solicitante_id: str
    monto: Optional[float] = None
    justificacion: str
    estado: Literal["pendiente", "aprobada", "rechazada"] = "pendiente"
    aprobador_id: Optional[str] = None
    fecha_resolucion: Optional[str] = None
    comentarios: Optional[str] = None

class AuthorizationCreate(AuthorizationBase):
    pass

class Authorization(AuthorizationBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Alert Models
class AlertBase(BaseModel):
    asset_id: str
    tipo: Literal["costo_elevado", "mantenimiento_vencido", "reemplazo_sugerido", "autorizacion_pendiente"]
    titulo: str
    mensaje: str
    prioridad: Literal["baja", "media", "alta", "critica"] = "media"
    leida: bool = False
    enviada_email: bool = False
    enviada_whatsapp: bool = False

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# File Models
class FileRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_name: str
    file_type: str
    entity_type: str
    entity_id: str
    uploaded_by: str
    file_path: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Asset Replacement Models
class AssetReplacementBase(BaseModel):
    old_asset_id: str
    new_asset_id: str
    motivo: str
    fecha_baja: str
    fotos_old_asset: Optional[List[str]] = []
    fotos_new_asset: Optional[List[str]] = []
    autorizacion_id: Optional[str] = None
    costo_total: float
    notas: Optional[str] = None


# Maintenance Plan Models (Planes de Mantenimiento Preventivo)
class MaintenancePlanBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    tipo_agrupacion: Literal["individual", "area", "sucursal", "selectivo"] = "individual"
    asset_ids: List[str] = []  # IDs de activos (para individual o selectivo)
    area_restaurante: Optional[str] = None  # Para agrupación por área
    sucursal: Optional[str] = None  # Para agrupación por sucursal
    frecuencia_dias: int  # Cada cuántos días se debe realizar
    proximo_mantenimiento: str  # Fecha del próximo mantenimiento
    activo: bool = True
    notificar_dias_antes: int = 7  # Días de anticipación para notificar
    notas: Optional[str] = None

class MaintenancePlanCreate(MaintenancePlanBase):
    pass

class MaintenancePlan(MaintenancePlanBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str
    ultimo_mantenimiento: Optional[str] = None

class AssetReplacementCreate(AssetReplacementBase):
    pass

class AssetReplacement(AssetReplacementBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str

# Dashboard Stats
class DashboardStats(BaseModel):
    total_assets: int
    assets_operativos: int
    assets_mantenimiento: int
    assets_criticos: int
    mantenimientos_pendientes: int
    autorizaciones_pendientes: int
    alertas_activas: int
    gasto_mes_actual: float
