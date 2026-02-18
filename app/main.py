from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import Session, select, text
from app.db.session import get_session, init_db
from app.core.config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create default user if not exists
    from app.db.session import engine
    from app.models.user import User
    from app.core import security
    
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == "admin")).first()
        if not user:
            print("Creating default admin user...")
            user = User(
                email="admin",
                password_hash=security.get_password_hash("spinner"),
                role="admin",
                is_active=True
            )
            session.add(user)
            session.commit()
            print("Default admin user created.")
            
    print("Startup complete")
    yield
    print("Shutdown complete")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

from app.api.v1.api import api_router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root(session: Session = Depends(get_session)):
    try:
        result = session.exec(text("SELECT 1")).one()
        return {"message": "Welcome to Stenella!", "db_status": "Connected", "validation": result}
    except Exception as e:
        return {"message": "Welcome to Stenella!", "db_status": "Error", "error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "ok"}
