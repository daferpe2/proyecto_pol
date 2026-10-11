from typing import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Session, SQLModel, create_engine

# from dotenv import load_dotenv

sqlite_name = "blogs.db"
sqlite_url = f"sqlite:///{sqlite_name}"

# load_dotenv()

# DATABASE_URL = os.environ.get("DATABASE_URL")
# engine = create_engine(DATABASE_URL,echo=True)
# engine = create_engine(sqlite_url,echo=True)

# engine = create_engine(engine,echo=True)


engine = create_engine(
    sqlite_url,
    echo=True,            # muestra SQL en consola
    connect_args={"check_same_thread": False}  # necesario para FastAPI
)

def create_tables(app:FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session,Depends(get_session)]
