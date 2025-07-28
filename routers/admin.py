from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Path, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import get_db
from models import Todos, Users
from modules.auth_modules.auth_crud import (
    get_all_users, get_user_detail_by_id, update_user_by_admin, delete_user_by_admin
)
from modules.auth_modules.auth_schemas import UserResponse, UserUpdateAdminRequest
from routers.auth import user_dependency, api_user_dependency  # Import cả hai user_dependency và api_user_dependency
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

db_dependency = Annotated[AsyncSession, Depends(get_db)]

templates = Jinja2Templates(directory="templates")


# --- Page Routes ---

@router.get("/all-todos-page")
async def render_admin_all_todos_page(request: Request, db: db_dependency,
                                      user: user_dependency):  # Page Route dùng user_dependency
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access Denied: Not an admin')

    result = await db.execute(select(Todos))
    todos = result.scalars().all()
    return templates.TemplateResponse("admin_todos.html", {"request": request, "todos": todos, "user": user})


@router.get("/users-page")
async def render_admin_users_page(request: Request, db: db_dependency,
                                  user: user_dependency):  # Page Route dùng user_dependency
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access Denied: Not an admin')

    users = await get_all_users(db)
    return templates.TemplateResponse("admin_users.html", {"request": request, "users": users, "user": user})


# --- API Endpoints ---

@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all_admin_todos(user: api_user_dependency, db: db_dependency):  # API Endpoint dùng api_user_dependency
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access Denied: Not an admin')

    result = await db.execute(select(Todos))
    return result.scalars().all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_admin(user: api_user_dependency,  # API Endpoint dùng api_user_dependency
                            db: db_dependency,
                            todo_id: int = Path(gt=0)):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access Denied: Not an admin')

    todo_model_result = await db.execute(select(Todos).filter(Todos.id == todo_id))
    todo_model = todo_model_result.scalars().first()

    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found.')

    await db.execute(delete(Todos).filter(Todos.id == todo_id))
    await db.commit()


@router.get("/users", status_code=status.HTTP_200_OK, response_model=List[UserResponse])
async def get_all_users_admin(user: api_user_dependency, db: db_dependency):  # API Endpoint dùng api_user_dependency
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access Denied: Not an admin')

    return await get_all_users(db)


@router.get("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_admin(user: api_user_dependency, db: db_dependency,
                         user_id: int = Path(gt=0)):  # API Endpoint dùng api_user_dependency
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access Denied: Not an admin')

    user_model = await get_user_detail_by_id(db, user_id)
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')
    return user_model


@router.put("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_user_admin(user: api_user_dependency,  # API Endpoint dùng api_user_dependency
                            db: db_dependency,
                            user_update_request: UserUpdateAdminRequest,
                            user_id: int = Path(gt=0)):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access Denied: Not an admin')

    user_model = await get_user_detail_by_id(db, user_id)
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')

    updated_user = await update_user_by_admin(db, user_model, user_update_request)
    return updated_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(user: api_user_dependency, db: db_dependency,
                            user_id: int = Path(gt=0)):  # API Endpoint dùng api_user_dependency
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access Denied: Not an admin')

    user_model = await get_user_detail_by_id(db, user_id)
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')

    await delete_user_by_admin(db, user_model)
