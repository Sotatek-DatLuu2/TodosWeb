from fastapi import FastAPI, Request, status
from routers import auth, todos, admin
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from database import init_db_async


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    await init_db_async()


@app.get("/")
async def test(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)






