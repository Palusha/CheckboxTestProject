from async_fastapi_jwt_auth import AuthJWT
from fastapi import status, APIRouter, Depends, HTTPException

from src.auth import service
from .schemas import AccessTokenResponse, AuthUser, RegisterUser, UserResponse

router = APIRouter()


@router.post(
    "/signup/", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
async def register_user(
    auth_data: RegisterUser,
) -> dict[str, str]:
    if await service.get_user_by_username(auth_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with '{auth_data.username}' username already exists.",
        )
    if await service.get_user_by_email(auth_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with '{auth_data.email}' email already exists.",
        )

    return await service.create_user(auth_data)


@router.post(
    "/login/", status_code=status.HTTP_201_CREATED, response_model=AccessTokenResponse
)
async def login(user: AuthUser, Authorize: AuthJWT = Depends()):
    user = await service.authenticate_user(user)

    access_token = await Authorize.create_access_token(subject=user.id)
    refresh_token = await Authorize.create_refresh_token(subject=user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh/", status_code=status.HTTP_201_CREATED)
async def refresh(Authorize: AuthJWT = Depends()):
    await Authorize.jwt_refresh_token_required()

    current_user = await Authorize.get_jwt_subject()
    new_access_token = await Authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}


@router.get("/me/")
async def user(Authorize: AuthJWT = Depends()):
    await Authorize.jwt_required()
    current_user = await Authorize.get_jwt_subject()
    return {"user_id": current_user}
