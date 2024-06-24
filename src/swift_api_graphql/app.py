from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from strawberry.fastapi import GraphQLRouter

from sqlalchemy.orm import Session

from .schema import schema
from .database import get_db, engine
from .models import Base

# Create the database tables
Base.metadata.create_all(bind=engine)

# Create the FastAPI app
app = FastAPI()

# CORS
origins = [
    # local testing with Angular
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Web API
@app.get("/", tags=["Root"])
async def get_root():
    return {"message": "Swift API GraphQL"}

@app.get("/ping", tags=["Root"])
async def ping():
    return "PONG"


def get_context(db: Session = Depends(get_db)):
    return {"db": db}

graphql_app = GraphQLRouter(schema, context_getter=get_context)

app.include_router(graphql_app, prefix="/graphql")

