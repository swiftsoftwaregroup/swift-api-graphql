import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from swift_api_graphql.app import app, get_db
from swift_api_graphql.models import Base, BookModel

# use in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

# use ./test.db SQLite database for testing
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def test_fixture():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def clean_table(test_fixture):
    db = TestingSessionLocal()
    db.query(BookModel).delete()
    db.commit()

def test_create_book(test_fixture):
    query = """
    mutation {
        createBook(book: {
            title: "Test Book",
            author: "Test Author",
            datePublished: "2023-01-01",
            coverImage: "http://example.com/cover.jpg"
        }) {
            id
            title
            author
            datePublished
            coverImage
        }
    }
    """
    response = test_fixture.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()["data"]["createBook"]
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"
    assert data["datePublished"] == "2023-01-01"
    assert data["coverImage"] == "http://example.com/cover.jpg"
    assert "id" in data

def test_read_books(test_fixture):
    # First, create a book
    create_query = """
    mutation {
        createBook(book: {
            title: "Test Book",
            author: "Test Author",
            datePublished: "2023-01-01",
            coverImage: "http://example.com/cover.jpg"
        }) {
            id
        }
    }
    """
    test_fixture.post("/graphql", json={"query": create_query})
    
    query = """
    query {
        books {
            id
            title
            author
            datePublished
            coverImage
        }
    }
    """
    response = test_fixture.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()["data"]["books"]
    assert len(data) == 1
    assert data[0]["title"] == "Test Book"

def test_read_book(test_fixture):
    # First, create a book
    create_query = """
    mutation {
        createBook(book: {
            title: "Test Book",
            author: "Test Author",
            datePublished: "2023-01-01",
            coverImage: "http://example.com/cover.jpg"
        }) {
            id
        }
    }
    """
    create_response = test_fixture.post("/graphql", json={"query": create_query})
    book_id = create_response.json()["data"]["createBook"]["id"]
    
    query = f"""
    query {{
        book(id: {book_id}) {{
            id
            title
            author
            datePublished
            coverImage
        }}
    }}
    """
    response = test_fixture.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()["data"]["book"]
    assert data["title"] == "Test Book"

def test_update_book(test_fixture):
    # First, create a book
    create_query = """
    mutation {
        createBook(book: {
            title: "Test Book",
            author: "Test Author",
            datePublished: "2023-01-01",
            coverImage: "http://example.com/cover.jpg"
        }) {
            id
        }
    }
    """
    create_response = test_fixture.post("/graphql", json={"query": create_query})
    book_id = create_response.json()["data"]["createBook"]["id"]
    
    update_query = f"""
    mutation {{
        updateBook(id: {book_id}, book: {{
            title: "Updated Book",
            author: "Updated Author",
            datePublished: "2023-02-01",
            coverImage: "http://example.com/updated_cover.jpg"
        }}) {{
            id
            title
            author
            datePublished
            coverImage
        }}
    }}
    """
    response = test_fixture.post("/graphql", json={"query": update_query})
    assert response.status_code == 200
    data = response.json()["data"]["updateBook"]
    assert data["title"] == "Updated Book"
    assert data["author"] == "Updated Author"
    assert data["datePublished"] == "2023-02-01"
    assert data["coverImage"] == "http://example.com/updated_cover.jpg"

def test_delete_book(test_fixture):
    # First, create a book
    create_query = """
    mutation {
        createBook(book: {
            title: "Test Book",
            author: "Test Author",
            datePublished: "2023-01-01",
            coverImage: "http://example.com/cover.jpg"
        }) {
            id
        }
    }
    """
    create_response = test_fixture.post("/graphql", json={"query": create_query})
    book_id = create_response.json()["data"]["createBook"]["id"]
    
    delete_query = f"""
    mutation {{
        deleteBook(id: {book_id})
    }}
    """
    response = test_fixture.post("/graphql", json={"query": delete_query})
    assert response.status_code == 200
    assert response.json()["data"]["deleteBook"] == True
    
    # Try to get the deleted book
    get_query = f"""
    query {{
        book(id: {book_id}) {{
            id
        }}
    }}
    """
    get_response = test_fixture.post("/graphql", json={"query": get_query})
    assert get_response.status_code == 200
    assert get_response.json()["data"]["book"] is None

def test_read_non_existent_book(test_fixture):
    query = """
    query {
        book(id: 999) {
            id
        }
    }
    """
    response = test_fixture.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert response.json()["data"]["book"] is None

def test_update_non_existent_book(test_fixture):
    query = """
    mutation {
        updateBook(id: 999, book: {
            title: "Updated Book",
            author: "Updated Author",
            datePublished: "2023-02-01",
            coverImage: "http://example.com/updated_cover.jpg"
        }) {
            id
        }
    }
    """
    response = test_fixture.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert response.json()["data"]["updateBook"] is None

def test_delete_non_existent_book(test_fixture):
    query = """
    mutation {
        deleteBook(id: 999)
    }
    """
    response = test_fixture.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert response.json()["data"]["deleteBook"] == False
    