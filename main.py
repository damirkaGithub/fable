from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from datetime import datetime





# Настройка базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./fable.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Swipe(Base):
    __tablename__ = "swipes"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, nullable=False)
    place_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    is_liked = Column(Boolean, nullable=False)
    swiped_at = Column(String, default=lambda: datetime.now().isoformat())  # Исправлено

    def __repr__(self):
        return f"<Swipe(place_id={self.place_id}, is_liked={self.is_liked})>"


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")

templates = Jinja2Templates(directory="templates")

places = [
    {
        "id": 1,
        "name": "Эрмитаж-Казань",
        "address": "Территория Кремль, 12",
        "lat": 55.798546,
        "lon": 49.105965,
        "image": "/images/ermitazh.jpg"
    },
    {
        "id": 2,
        "name": "Музей истории Благовещенского собора",
        "address": "Вахитовский район, территория Кремль, 2",
        "lat": 55.799997,
        "lon": 49.107340,
        "image": "/images/sobor.jpg"
    },
    {
        "id": 3,
        "name": "Руины башни монастырской стены",
        "address": "Большая Красная ул., 1Б",
        "lat": 55.799575,
        "lon": 49.111058,
        "image": "/images/tower.jpg"
    },
]


@app.get("/slides/", response_class=HTMLResponse)
async def slides_page(request: Request):
    return templates.TemplateResponse(
        "slides.html",
        {
            "request": request,
            "places": places,
        }
    )


@app.post("/like/{place_id}")
async def like_place(
        place_id: int,
        db: Session = Depends(get_db)
):
    place = next((p for p in places if p["id"] == place_id), None)
    if not place:
        return {"status": "error", "message": "Place not found"}

    try:
        db_swipe = Swipe(
            place_id=place["id"],
            place_name=place["name"],
            address=place["address"],
            lat=place["lat"],
            lon=place["lon"],
            is_liked=True
        )
        db.add(db_swipe)
        db.commit()
        return {"status": "liked", "place_id": place_id}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


@app.post("/dislike/{place_id}")
async def dislike_place(
        place_id: int,
        db: Session = Depends(get_db)
):
    place = next((p for p in places if p["id"] == place_id), None)
    if not place:
        return {"status": "error", "message": "Place not found"}

    try:
        db_swipe = Swipe(
            place_id=place["id"],
            place_name=place["name"],
            address=place["address"],
            lat=place["lat"],
            lon=place["lon"],
            is_liked=False
        )
        db.add(db_swipe)
        db.commit()
        return {"status": "disliked", "place_id": place_id}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}