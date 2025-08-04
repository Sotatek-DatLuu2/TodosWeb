from fastapi import FastAPI, Request, status
from routers import auth, todos, admin
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse


from services.initial_setup import seed_initial_admin_user

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    await seed_initial_admin_user()


@app.get("/")
async def test(request: Request):
    return RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)

