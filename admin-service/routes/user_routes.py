from config.database import get_db
from fastapi import APIRouter, Depends, status, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from controllers.user_controller import UserController
from models.schema import UserOnboard, UserLogin, UserUpdate

# User router
user_router = APIRouter(prefix="/user", tags=["users"])


@user_router.post("/onboard")
def onboard_user(user_data: UserOnboard, db: Session = Depends(get_db)):
    try:
        user_instance = UserController(db)
        response = user_instance.create_user(user_data.model_dump())
        return JSONResponse(
            content=response,
            media_type="application/json",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_router.post("/login")
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    try:
        user_instance = UserController(db)
        response = user_instance.login_user(user_login.email, user_login.password)
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
def get_user_profile(
    user_id: str = Query(...),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    user_instance = UserController(db)
    try:
        user_profile = user_instance.get_user_profile(user_id, authorization)
        return JSONResponse(content=user_profile, status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )


@user_router.put("/update")
def update_user(
    data: UserUpdate,
    user_id: str = Query(...),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    user_instance = UserController(db)
    try:
        data_to_update = data.model_dump(exclude_unset=True)
        update_response = user_instance.update_user(
            user_id, authorization, data_to_update
        )
        return JSONResponse(content=update_response, status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )
