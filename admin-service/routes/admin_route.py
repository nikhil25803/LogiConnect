from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from config.database import get_db
from models.schema import AdminLogin
from controllers.admin_controller import AdminController

# Admin login router
admin_route = APIRouter(prefix="/admin", tags=["admin"])


@admin_route.post("/login", response_model=dict)
async def login_admin(admin_data: AdminLogin, db: AsyncSession = Depends(get_db)):
    try:
        admin_instance = AdminController(db)
        response = await admin_instance.login_admin(
            email=admin_data.email, password=admin_data.password
        )
        return JSONResponse(
            content=response,
            media_type="application/json",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to admin login.",
        )
