from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from database import SessionLocal, engine, get_db
from models import Prod
import database_models


# --------------------------------------------------
# Database Initialization and Seeding
# --------------------------------------------------

def init_db():
    database_models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        count = db.scalar(
            select(func.count()).select_from(database_models.Prod)
        )

        if count == 0:
            initial_products = [
                Prod(id=1, name="Product 1", description="First product", price=10.0, quantity=5),
                Prod(id=2, name="Product 2", description="Second product", price=20.0, quantity=10),
                Prod(id=3, name="Product 3", description="Third product", price=30.0, quantity=15),
                Prod(id=4, name="Product 4", description="Fourth product", price=40.0, quantity=20),
                Prod(id=5, name="Product 5", description="Fifth product", price=50.0, quantity=25),
                Prod(id=6, name="Product 6", description="Sixth product", price=60.0, quantity=30),
            ]

            db.add_all([
                database_models.Prod(**product.model_dump())
                for product in initial_products
            ])

            db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

appbe = FastAPI(
    title="Product Management API",
    description="REST API for managing products using FastAPI and PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)


# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------

appbe.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Helper Function
# --------------------------------------------------

def serialize_product(product):
    return Prod.model_validate(
        product,
        from_attributes=True
    )


# --------------------------------------------------
# Home and Documentation Routes
# --------------------------------------------------

@appbe.get("/")
def greet():
    return {"message": "Hello, this is the Home Page"}


@appbe.get("/doc")
def doc():
    return {"message": "This is the API documentation endpoint"}


# --------------------------------------------------
# GET - Retrieve All Products
# --------------------------------------------------

@appbe.get("/prod", response_model=list[Prod])
def get_all_prods(db: Session = Depends(get_db)):

    products = db.scalars(
        select(database_models.Prod)
    ).all()

    return [
        serialize_product(product)
        for product in products
    ]


# --------------------------------------------------
# GET - Retrieve Product by ID
# --------------------------------------------------

@appbe.get("/prod/{id}", response_model=Prod)
def get_prod_id(id: int, db: Session = Depends(get_db)):

    product = db.get(database_models.Prod, id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return serialize_product(product)


# --------------------------------------------------
# POST - Add New Product
# --------------------------------------------------

@appbe.post(
    "/prod",
    response_model=Prod,
    status_code=status.HTTP_201_CREATED
)
def add_prod(prod: Prod, db: Session = Depends(get_db)):

    db_prod = database_models.Prod(**prod.model_dump())

    try:
        db.add(db_prod)
        db.commit()
        db.refresh(db_prod)

        return serialize_product(db_prod)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


# --------------------------------------------------
# PUT - Update Existing Product
# --------------------------------------------------

@appbe.put("/prod/{id}", response_model=Prod)
def update_prod(
    id: int,
    prod: Prod,
    db: Session = Depends(get_db)
):

    db_prod = db.get(database_models.Prod, id)

    if not db_prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    try:
        for key, value in prod.model_dump().items():
            setattr(db_prod, key, value)

        db.commit()
        db.refresh(db_prod)

        return serialize_product(db_prod)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product"
        )


# --------------------------------------------------
# DELETE - Remove Product
# --------------------------------------------------

@appbe.delete("/prod/{id}")
def delete_prod(id: int, db: Session = Depends(get_db)):

    db_prod = db.get(database_models.Prod, id)

    if not db_prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    try:
        db.delete(db_prod)
        db.commit()

        return {
            "message": "Product deleted successfully",
            "product_id": id
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )
