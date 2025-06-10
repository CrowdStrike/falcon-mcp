"""Falcon host operations core functionality."""

from typing import Optional
import structlog
from .falcon_client import FalconClient
from .host_manager import HostManager

logger = structlog.get_logger(__name__)

# Global instances
_falcon_client: Optional[FalconClient] = None
_host_manager: Optional[HostManager] = None


def initialize_falcon_services(client_id: Optional[str] = None, 
                             client_secret: Optional[str] = None,
                             base_url: Optional[str] = None) -> None:
    """Initialize Falcon services.
    
    Args:
        client_id: Falcon API client ID
        client_secret: Falcon API client secret
        base_url: Falcon API base URL
    """
    global _falcon_client, _host_manager
    
    logger.info("initializing_falcon_services")
    _falcon_client = FalconClient(client_id, client_secret, base_url)
    _host_manager = HostManager(_falcon_client)
    logger.info("falcon_services_initialized")


def get_host_manager() -> HostManager:
    """Get the initialized host manager.
    
    Returns:
        HostManager instance
        
    Raises:
        RuntimeError: If services not initialized
    """
    if _host_manager is None:
        raise RuntimeError("Falcon services not initialized. Call initialize_falcon_services() first.")
    return _host_manager 