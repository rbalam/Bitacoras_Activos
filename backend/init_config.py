#!/usr/bin/env python3
"""
Script para inicializar configuraciones en la base de datos
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
import uuid

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def init_configs():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Default configurations
    configs = [
        # Twilio
        {
            "id": str(uuid.uuid4()),
            "key": "TWILIO_ACCOUNT_SID",
            "value": "ACc41b705a355130d7d5e73920dd9d23b1",
            "category": "twilio",
            "description": "Twilio Account SID",
            "is_sensitive": True,
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "key": "TWILIO_AUTH_TOKEN",
            "value": "b64b2400dee6f1d990cec096a7d46a0d",
            "category": "twilio",
            "description": "Twilio Auth Token",
            "is_sensitive": True,
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "key": "TWILIO_WHATSAPP_FROM",
            "value": "+14155238886",
            "category": "twilio",
            "description": "Twilio WhatsApp Number",
            "is_sensitive": False,
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        # Resend
        {
            "id": str(uuid.uuid4()),
            "key": "RESEND_API_KEY",
            "value": "",
            "category": "email",
            "description": "Resend API Key for email notifications",
            "is_sensitive": True,
            "active": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "key": "SENDER_EMAIL",
            "value": "onboarding@resend.dev",
            "category": "email",
            "description": "Email sender address",
            "is_sensitive": False,
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Check if configs already exist
    existing_count = await db.configs.count_documents({})
    
    if existing_count > 0:
        print(f"⚠️  Ya existen {existing_count} configuraciones en la base de datos")
        response = input("¿Deseas reemplazarlas? (s/N): ")
        if response.lower() != 's':
            print("❌ Operación cancelada")
            client.close()
            return
        
        # Delete existing configs
        result = await db.configs.delete_many({})
        print(f"🗑️  Eliminadas {result.deleted_count} configuraciones anteriores")
    
    # Insert new configs
    result = await db.configs.insert_many(configs)
    print(f"✅ {len(result.inserted_ids)} configuraciones inicializadas correctamente")
    
    print("\n📋 Configuraciones creadas:")
    for config in configs:
        status = "✓ Activo" if config["active"] else "✗ Inactivo"
        value_display = config["value"][:10] + "..." if config["is_sensitive"] and config["value"] else config["value"]
        print(f"  • {config['key']}: {value_display} [{status}]")
    
    client.close()
    print("\n✨ Inicialización completada")

if __name__ == "__main__":
    asyncio.run(init_configs())
