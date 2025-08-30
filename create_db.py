# Letzte bearbeitung 30.08
from database import engine
from models import Base

Base.metadata.create_all(bind=engine)
print("✅ Tabellen erstellt")