from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, user, contact, language
from app.routers import stack, project

app = FastAPI(title="Portafolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(contact.router)
app.include_router(language.router)
app.include_router(stack.router)
app.include_router(project.router)
