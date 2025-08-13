from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.config import CORSSettings


class CORSConfigMiddleware(BaseHTTPMiddleware):
    """Middleware to configure CORS (Cross-Origin Resource Sharing) for the FastAPI application.
    
    This middleware allows cross-origin requests from specified origins, which is essential
    for frontend applications running on different ports or domains.
    
    Parameters
    ----------
    app: FastAPI
        The FastAPI application instance.
    cors_settings: CORSSettings
        Configuration settings for CORS behavior.
    
    Attributes
    ----------
    cors_settings: CORSSettings
        The CORS configuration settings.
    
    Note
    ----
        - CORS is essential for web applications that need to make requests from different origins
        - This middleware should be added early in the middleware stack
        - The middleware automatically handles preflight OPTIONS requests
    """
    
    def __init__(self, app: FastAPI, cors_settings: CORSSettings) -> None:
        super().__init__(app)
        self.cors_settings = cors_settings
    
    def configure_cors(self, app: FastAPI) -> None:
        """Configure CORS middleware on the FastAPI application.
        
        Parameters
        ----------
        app: FastAPI
            The FastAPI application instance to configure.
            
        Note
        ----
            - This method adds the CORSMiddleware to the application
            - The middleware is configured with the settings from CORSSettings
            - CORS is only enabled if CORS_ENABLED is True in settings
        """
        if not self.cors_settings.CORS_ENABLED:
            return
            
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.cors_settings.CORS_ALLOW_ORIGINS,
            allow_credentials=self.cors_settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=self.cors_settings.CORS_ALLOW_METHODS,
            allow_headers=self.cors_settings.CORS_ALLOW_HEADERS,
            expose_headers=self.cors_settings.CORS_EXPOSE_HEADERS,
            max_age=self.cors_settings.CORS_MAX_AGE,
        )


def add_cors_middleware(app: FastAPI, cors_settings: CORSSettings) -> None:
    """Helper function to add CORS middleware to a FastAPI application.
    
    Parameters
    ----------
    app: FastAPI
        The FastAPI application instance.
    cors_settings: CORSSettings
        The CORS configuration settings.
        
    Note
    ----
        - This is a convenience function that creates and configures CORS middleware
        - It's designed to be used in the application setup process
        - The middleware is added with the highest priority (first in the stack)
    """
    cors_middleware = CORSConfigMiddleware(app, cors_settings)
    cors_middleware.configure_cors(app)
