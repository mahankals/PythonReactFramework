from fastapi import APIRouter

admin_router = APIRouter()

# Import admin submodules
def _include_admin_routes():
    from app.api.admin import users as admin_users
    from app.api.admin import rbac as admin_rbac
    from app.api.admin import config as admin_config

    admin_router.include_router(admin_users.router, prefix="/users", tags=["Admin - Users"])
    admin_router.include_router(admin_rbac.router, prefix="/rbac", tags=["Admin - RBAC"])
    admin_router.include_router(admin_config.router, prefix="/config", tags=["Admin - Configuration"])

_include_admin_routes()
