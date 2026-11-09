"""
API Gateway package initializer.

This file ensures Python recognizes the api_gateway directory as a package.
Routers, middleware, and server components can be imported cleanly from here.
"""

# Optional: expose commonly used modules for cleaner imports
from .server import app
