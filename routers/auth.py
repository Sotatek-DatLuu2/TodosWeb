from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from database import get_db
from modules.auth_modules.auth_schemas import (
    CreateUserRequest, Token, ForgotPasswordRequest,
    ResetPasswordRequest, ChangePasswordRequest
)
from modules.auth_modules.auth_utils import (
    verify_password, create_access_token, decode_access_token,
    send_password_reset_email
)
from modules.auth_modules.auth_crud import (
    get_user_by_username, get_user_by_email, create_user,
    save_password_reset_token, get_password_reset_token_entry,
    delete_password_reset_token_entry, update_user_password,
    get_user_by_id
)

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# OAuth2PasswordBearer này vẫn sẽ được dùng cho API endpoint.
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

db_dependency = Annotated[AsyncSession, Depends(get_db)]

templates = Jinja2Templates(directory="templates")


# --- AUTHENTICATION DEPENDENCIES ---
# Hàm này sẽ được dùng cho các Page Routes (trả về HTML)
# Nó sẽ đọc token từ cookie
async def get_user_from_request(request: Request) -> dict:
    token_from_cookie = request.cookies.get("access_token")

    if not token_from_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication token missing (cookie)")

    user_data = decode_access_token(token_from_cookie)
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials (cookie)")

    return user_data


# Hàm này sẽ được dùng cho các API Endpoints (trả về JSON)
# Nó sẽ đọc token từ Authorization header (Bearer token)
async def get_authenticated_api_user(token: Annotated[str, Depends(oauth2_bearer)]) -> dict:
    user_data = decode_access_token(token)  # decode_access_token sẽ raise HTTPException nếu lỗi
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials (header)")

    return user_data


# user_dependency cho Page Routes (sử dụng token từ cookie)
user_dependency = Annotated[dict, Depends(get_user_from_request)]

# api_user_dependency cho API Endpoints (sử dụng token từ Authorization header)
api_user_dependency = Annotated[dict, Depends(get_authenticated_api_user)]


# --- AUTHENTICATE USER FUNCTION (Bổ sung vào đây) ---
# Hàm này dùng để xác thực username/password với database
async def authenticate_user(username: str, password: str, db: AsyncSession):
    user = await get_user_by_username(db, username)  # Gọi hàm CRUD từ auth_crud
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        return False
    return user


# --- Page Routes ---
@router.get("/login-page")
async def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register-page")
async def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/forgot-password-page")
async def render_forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@router.get("/reset-password-page")
async def render_reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})


@router.get("/change-password-page")
async def render_change_password_page(request: Request, user: user_dependency):
    return templates.TemplateResponse("change_password.html", {"request": request, "user": user})


# --- API Endpoints ---

@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, create_user_request: CreateUserRequest):
    if await get_user_by_email(db, create_user_request.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already exists.')
    if await get_user_by_username(db, create_user_request.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exists.')

    try:
        await create_user(db, create_user_request)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi đăng ký người dùng: {str(e)}"
        )
    return {"message": "User registered successfully."}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    # GỌI HÀM AUTHENTICATE_USER ĐÃ ĐƯỢC BỔ SUNG
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=30))
    # Đã thêm user.role vào phản hồi
    return {'access_token': token, 'token_type': 'bearer', 'user_role': user.role}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password_endpoint(request: ForgotPasswordRequest, db: db_dependency):
    user = await get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="If an account with that email exists, a password reset link has been sent.")

    token = await save_password_reset_token(db, user.id)
    send_password_reset_email(user.email, user.first_name, token)

    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_endpoint(request: ResetPasswordRequest, db: db_dependency):
    reset_token_entry = await get_password_reset_token_entry(db, request.token)

    if not reset_token_entry or datetime.utcnow() > reset_token_entry.expires_at:
        if reset_token_entry:
            await delete_password_reset_token_entry(db, reset_token_entry)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token.")

    user = await get_user_by_id(db, reset_token_entry.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    await update_user_password(db, user, request.new_password)
    await delete_password_reset_token_entry(db, reset_token_entry)

    return {"message": "Password has been reset successfully."}


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password_endpoint(
        request: ChangePasswordRequest,
        db: db_dependency,
        current_user: api_user_dependency  # Đã thay đổi sang api_user_dependency vì đây là API endpoint
):
    user_id = current_user.get("id")
    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if not verify_password(request.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid current password.")

    await update_user_password(db, user, request.new_password)

    return {"message": "Password has been changed successfully."}
