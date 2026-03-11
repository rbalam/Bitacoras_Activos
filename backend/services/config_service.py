from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ConfigService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._cache: Dict[str, str] = {}
        self._cache_loaded = False
    
    async def load_cache(self):
        """Load all active configs into memory cache"""
        configs = await self.db.configs.find({"active": True}, {"_id": 0}).to_list(1000)
        self._cache = {config["key"]: config["value"] for config in configs}
        self._cache_loaded = True
        logger.info(f"Loaded {len(self._cache)} configs into cache")
    
    async def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get config value by key"""
        if not self._cache_loaded:
            await self.load_cache()
        return self._cache.get(key, default)
    
    async def set(self, key: str, value: str, user_id: str = None) -> bool:
        """Set or update config value"""
        from datetime import datetime, timezone
        
        existing = await self.db.configs.find_one({"key": key}, {"_id": 0})
        
        if existing:
            await self.db.configs.update_one(
                {"key": key},
                {
                    "$set": {
                        "value": value,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "updated_by": user_id
                    }
                }
            )
        else:
            # This shouldn't happen in normal operation, but handle it
            logger.warning(f"Config key {key} not found, creating new entry")
            return False
        
        # Update cache
        self._cache[key] = value
        return True
    
    async def reload_cache(self):
        """Reload cache from database"""
        await self.load_cache()
    
    async def get_twilio_config(self) -> Dict[str, Optional[str]]:
        """Get Twilio configuration"""
        return {
            "account_sid": await self.get("TWILIO_ACCOUNT_SID"),
            "auth_token": await self.get("TWILIO_AUTH_TOKEN"),
            "whatsapp_from": await self.get("TWILIO_WHATSAPP_FROM")
        }
    
    async def get_resend_config(self) -> Dict[str, Optional[str]]:
        """Get Resend email configuration"""
        return {
            "api_key": await self.get("RESEND_API_KEY"),
            "sender_email": await self.get("SENDER_EMAIL")
        }
