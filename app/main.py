from fastapi import FastAPI
from app.routers import auth,user, contact

app = FastAPI(title="Portafolio API", version="1.0.0")

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(contact.router)


@app.get("/", tags=["Health"]) 
def health_check(): 
    return {"status": "ok"}

