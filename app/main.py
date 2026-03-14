from fastapi import FastAPI
from app.routers import auth, user, contact, language
from app.routers import stack, project

app = FastAPI(title="Portafolio API", version="1.0.0")

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(contact.router)
app.include_router(language.router)
app.include_router(stack.router)
app.include_router(project.router)
