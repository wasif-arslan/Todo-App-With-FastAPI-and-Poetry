from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated, Optional
from todoapp import setting

app: FastAPI = FastAPI()

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str

class TodoCreate(SQLModel):
    name: str
    description: str

class TodoResponse(SQLModel):
    id: int
    name: str
    description: str


connection_string:str = str(setting.DATABASE_URL).replace("postgresql", "postgresql+psycopg")
engine = create_engine(connection_string, connect_args={"sslmode":"require"}, pool_recycle=300, pool_size=10)

SQLModel.metadata.create_all(engine)

def get_data():
    with Session(engine) as session:
        yield session

@app.get("/todos")
def get_all(db: Annotated[Session, Depends(get_data)]):
    todos = db.exec(select(Todo)).all()
    return todos

@app.post("/todos", response_model=TodoCreate)
def create_todo(todo: TodoCreate, db: Session = Depends(get_data)):
    db_todo = Todo.model_validate(todo)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def read_todo(todo_id: int, db: Session = Depends(get_data)):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def update_hero(todo_id: int, todo: TodoResponse):
    with Session(engine) as session:
        db_todo = session.get(Todo, todo_id)
        if not db_todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        todo_data = todo.model_dump(exclude_unset=True)
        db_todo.sqlmodel_update(todo_data)
        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)
        return db_todo
    
@app.delete("/todos/{todo_id}")
def delete_hero(todo_id: int):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        session.delete(todo)
        session.commit()
        return {"message": "Todo deleted successfully"}
    
    
    
    