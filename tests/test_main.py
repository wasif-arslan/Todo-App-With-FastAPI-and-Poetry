from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from todoapp.main import app, Todo, TodoCreate, TodoResponse, engine
from todoapp import setting


# # Set up a test database
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

connection_string:str = str(setting.DATABASE_URL).replace("postgresql", "postgresql+psycopg")
engine = create_engine(connection_string)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_data():
    with TestingSessionLocal() as session:
        yield session

# Override the get_data dependency
def override_get_data():
    with TestingSessionLocal() as session:
        yield session

# Create tables in the test database
def create_test_tables():
    Todo.metadata.create_all(engine)

# Drop tables after testing
def drop_test_tables():
    Todo.metadata.drop_all(engine)

# Initialize test client
client = TestClient(app)

# Test cases
def test_create_todo():
    create_test_tables()
    todo_data = {"name": "Test Todo", "description": "Test Description"}
    response = client.post("/todos", json=todo_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Todo"
    assert response.json()["description"] == "Test Description"
    drop_test_tables()

def test_get_all_todos():
    create_test_tables()
    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 0
    drop_test_tables()

def test_read_todo():
    create_test_tables()
    response = client.get("/todos/2")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Todo"
    assert response.json()["description"] == "Test Description"
    drop_test_tables()

def test_update_todo():
    create_test_tables()
    todo_data = {"name": "Updated Todo", "description": "Updated Description"}
    response = client.patch("/todos/2", json=todo_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Todo"
    assert response.json()["description"] == "Updated Description"
    drop_test_tables()

def test_delete_todo():
    create_test_tables()
    response = client.delete("/todos/2")
    assert response.status_code == 200
    assert response.json()["message"] == "Todo deleted successfully"
    drop_test_tables()
    
    
    
    
# Run the tests
# test_create_todo()
# test_get_all_todos()
# test_read_todo()
# test_update_todo()
# test_delete_todo()
