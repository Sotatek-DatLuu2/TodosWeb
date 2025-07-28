from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Todos
from modules.todos_modules.todo_schemas import TodoRequest

async def get_all_todos_for_user(db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Todos)
        .filter(Todos.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_todo_by_id_for_user(db: AsyncSession, todo_id: int, owner_id: int):
    result = await db.execute(
        select(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == owner_id)
    )
    return result.scalars().first()

async def create_new_todo(db: AsyncSession, todo_request: TodoRequest, owner_id: int):
    todo_model = Todos(**todo_request.model_dump(), owner_id=owner_id)
    db.add(todo_model)
    await db.commit()
    await db.refresh(todo_model)
    return todo_model

async def update_existing_todo(db: AsyncSession, todo_model: Todos, todo_request: TodoRequest):
    for field, value in todo_request.model_dump(exclude_unset=True).items():
        setattr(todo_model, field, value)
    db.add(todo_model)
    await db.commit()
    await db.refresh(todo_model)
    return todo_model

async def delete_existing_todo(db: AsyncSession, todo_model: Todos):
    await db.delete(todo_model)
    await db.commit()

