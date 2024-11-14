from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import List, Optional
from uvicorn import run

app = FastAPI()

# SQLite Database URL
DATABASE_URL = "sqlite:///development.db"

engine = create_engine(DATABASE_URL, echo=True)


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    price: float


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# Route to create a new item
@app.post("/items/", response_model=Item)
def create_item(item: Item, session: Session = Depends(get_session)):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


# Route to read all items
@app.get("/items/", response_model=List[Item])
def read_items(session: Session = Depends(get_session)):
    items = session.exec(select(Item)).all()
    return items


# Route to read an item by ID
@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# Route to update an item by ID
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updated_item: Item, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.name = updated_item.name
    item.description = updated_item.description
    item.price = updated_item.price
    session.commit()
    session.refresh(item)
    return item


# Route to delete an item by ID
@app.delete("/items/{item_id}", response_model=Item)
def delete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return item

if __name__ == "__main__":
    run(app, host="localhost", port=5000, log_level="debug")