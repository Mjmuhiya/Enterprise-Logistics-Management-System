import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Role

TEST_DATABASE_URL = "sqlite://"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    db.add_all([Role(name=name) for name in ["ADMIN", "CUSTOMER", "DRIVER", "WAREHOUSE_OFFICER", "OPERATIONS_MANAGER", "FINANCE_OFFICER"]])
    db.commit()
    db.close()

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
