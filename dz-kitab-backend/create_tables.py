from app.database import engine, Base
from app.models.user import User  # import all models so SQLAlchemy sees them

# Create tables in PostgreSQL
Base.metadata.create_all(bind=engine)
print("Tables created in PostgreSQL!")
