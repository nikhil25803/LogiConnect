from config.database import get_db
from fastapi import APIRouter, Depends, status, HTTPException, Query, Header
from fastapi.responses import JSONResponse
from controllers.user_controller import UserController
from models.schema import UserOnboard, UserLogin
from sqlalchemy.ext.asyncio import AsyncSession

# User router
user_router = APIRouter(prefix="/user", tags=["users"])


@user_router.post("/onboard", response_model=dict)
async def onboard_user(user_data: UserOnboard, db: AsyncSession = Depends(get_db)):
    try:
        user_instance = UserController(db)
        response = await user_instance.create_user(user_data.model_dump())
        return JSONResponse(
            content=response,
            media_type="application/json",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_router.post("/login", response_model=dict)
async def login_user(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        user_instance = UserController(db)
        response = await user_instance.login_user(
            user_login.email, user_login.password
        )
        return JSONResponse(
            content=response,
            media_type="application/json",
            status_code=status.HTTP_200_OK,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_router.get("/profile")
async def get_user_profile(
    user_id: str = Query(...),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    user_instance = UserController(db)
    try:
        user_profile = await user_instance.get_user_profile(user_id, authorization)
        return JSONResponse(content=user_profile, status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )

