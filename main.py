from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal as DBSession, engine
from models import Prod
import database_models
from sqlalchemy.orm import Session
from database import get_db

appbe = FastAPI()

appbe.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)
database_models.Base.metadata.create_all(bind=engine)

@appbe.get("/")
def greet():
    return "Hello this Home Page"

@appbe.get("/doc")
def doc():
    return "This is Documentation for the API"


@appbe.get("/prod")
def get_all_prods(db: Session = Depends(get_db)):
    db_prods = db.query(database_models.Prod).all()
    return db_prods

prods = [
    Prod(id=1, name="Product 1", description="First product", price=10.0, quantity=5),
    Prod(id=2, name="Product 2", description="Second product", price=20.0, quantity=10),
    Prod(id=3, name="Product 3", description="Third product", price=30.0, quantity=15),
    Prod(id=4, name="Product 4", description="Fourth product", price=40.0, quantity=20),
    Prod(id=5, name="Product 5", description="Fifth product", price=50.0, quantity=25),
    Prod(id=6, name="Product 6", description="Sixth product", price=60.0, quantity=30)
]



def init_db():
    db = DBSession()

    count = db.query(database_models.Prod).count()
    if count == 0:
        for prod in prods:
            db.add(database_models.Prod(**prod.model_dump()))
        db.commit()

init_db()
    
    

@appbe.get("/prod/{id}")
def get_prod_id(id: int, db: Session = Depends(get_db)):
    db_prod = db.query(database_models.Prod).filter(database_models.Prod.id == id).first()
    if db_prod:
        return db_prod
    return "Product not found"

@appbe.post("/prod")
def add_prod(prod: Prod, db: Session = Depends(get_db)):
    db.add(database_models.Prod(**prod.model_dump()))
    db.commit()
    return prod

@appbe.put("/prod/{id}")
def update_prod(id: int, prod: Prod, db: Session = Depends(get_db)):
    db_prod = db.query(database_models.Prod).filter(database_models.Prod.id == id).first()
    if db_prod: 
        db_prod.name = prod.name
        db_prod.description = prod.description
        db_prod.price = prod.price
        db_prod.quantity = prod.quantity
        db.commit()
        return "Product updated"
    else:
        return "Product not found"

@appbe.delete("/prod/{id}")
def delete_prod(id: int, db: Session = Depends(get_db)):
    db_prod = db.query(database_models.Prod).filter(database_models.Prod.id == id).first()
    if db_prod:
        db.delete(db_prod)
        db.commit()
        return "Product deleted successfully"
    else:
        return "Produc t not found"
    