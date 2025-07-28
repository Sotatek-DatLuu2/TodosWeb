from typing import Annotated, List # Added List for future use if needed
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from database import get_db
from models import Todos
from modules.todos_modules.todo_schemas import TodoRequest
from modules.todos_modules.todo_crud import (
    get_all_todos_for_user, get_todo_by_id_for_user,
    create_new_todo, update_existing_todo, delete_existing_todo
)
from routers.auth import user_dependency, api_user_dependency # Import cả hai user_dependency và api_user_dependency

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

db_dependency = Annotated[AsyncSession, Depends(get_db)]


### Pages ###

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency, user: user_dependency): # Page Route dùng user_dependency
    """
    Render trang hiển thị danh sách Todos của người dùng.
    """
    todos = await get_all_todos_for_user(db, user.get('id'))
    return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})


@router.get("/add-todo-page")
async def render_add_todo_page(request: Request, db: db_dependency, user: user_dependency): # Page Route dùng user_dependency
    """
    Render trang thêm Todo mới.
    """
    return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, db: db_dependency, todo_id: int, user: user_dependency): # Page Route dùng user_dependency
    """
    Render trang chỉnh sửa Todo.
    """
    todo = await get_todo_by_id_for_user(db, todo_id, user.get('id'))
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found or not owned by user.")

    return templates.TemplateResponse("edit-todo.html",
                                      {"request": request, "todo": todo, "user": user}
                                      )


### API Endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_todos(user: api_user_dependency, db: db_dependency, # API Endpoint dùng api_user_dependency
                         skip: int = Query(0, ge=0),
                         limit: int = Query(100, gt=0, le=200)):
    """
    Lấy tất cả Todos của người dùng hiện tại.
    """
    return await get_all_todos_for_user(db, user.get('id'), skip=skip, limit=limit)


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_single_todo(user: api_user_dependency, # API Endpoint dùng api_user_dependency
                           db: db_dependency,
                           todo_id: int = Path(gt=0)):
    """
    Lấy một Todo cụ thể của người dùng hiện tại.
    """
    todo_model = await get_todo_by_id_for_user(db, todo_id, user.get('id'))
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo_item(user: api_user_dependency, # API Endpoint dùng api_user_dependency
                           db: db_dependency,
                           todo_request: TodoRequest):
    """
    Tạo một Todo mới cho người dùng hiện tại.
    """
    await create_new_todo(db, todo_request, user.get('id'))
    return {"message": "Todo created successfully."}


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo_item(user: api_user_dependency, # API Endpoint dùng api_user_dependency
                           db: db_dependency,
                           todo_id: int,
                           todo_request: TodoRequest):
    """
    Cập nhật một Todo hiện có của người dùng hiện tại.
    """
    todo_model = await get_todo_by_id_for_user(db, todo_id, user.get('id'))
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")

    await update_existing_todo(db, todo_model, todo_request)


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_item(user: api_user_dependency, # API Endpoint dùng api_user_dependency
                           db: db_dependency, todo_id: int = Path(gt=0)):
    """
    Xóa một Todo của người dùng hiện tại.
    """
    todo_model = await get_todo_by_id_for_user(db, todo_id, user.get('id'))
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")

    await delete_existing_todo(db, todo_model)
