# backend/app/main.py
"""FastAPI backend entry point for Finance Tracker.
Provides CRUD endpoints for transactions, budgets, and savings goals.
All data is stored in-memory for offline use; could be persisted to a JSON file if desired.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import json
import os

from .config import settings

from fastapi import Header, Depends

def verify_api_key(x_api_key: str = Header(None)):
    if settings.API_KEY and x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

app = FastAPI(title="Finance Tracker Backend", version="0.1.0")

# Allow frontend (localhost) to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== Pydantic Schemas ==== #
class Transaction(BaseModel):
    id: str
    type: Literal["income", "expense"]
    amount: float
    category: str
    description: Optional[str] = ""
    date: str  # ISO date string
    recurring: bool = False
    recurringPattern: Optional[Literal["daily", "weekly", "monthly", "yearly"]] = None

class Budget(BaseModel):
    id: str
    category: str
    monthYear: str  # e.g., "2024-09"
    limit: float
    alerts: bool = True

class Goal(BaseModel):
    id: str
    name: str
    targetAmount: float
    currentAmount: float = 0.0
    targetDate: str  # ISO date
    category: str
    priority: Literal["low", "medium", "high"]

# ==== In‑memory stores (could later be persisted to JSON) ==== #
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"transactions": [], "budgets": [], "goals": []}

def save_data(store):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)

_store = load_data()

# ==== Helper functions ==== #
def _find_item(collection: List[dict], item_id: str):
    for i, item in enumerate(collection):
        if item["id"] == item_id:
            return i, item
    return None, None

# ==== Transaction Endpoints ==== #
@app.get("/transactions", response_model=List[Transaction])
def get_transactions():
    return _store["transactions"]

@app.post("/transactions", response_model=Transaction)
def create_transaction(tx: Transaction):
    _store["transactions"].insert(0, tx.dict())
    save_data(_store)
    return tx

@app.put("/transactions/{tx_id}", response_model=Transaction)
def update_transaction(tx_id: str, tx: Transaction):
    idx, _ = _find_item(_store["transactions"], tx_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    _store["transactions"][idx] = tx.dict()
    save_data(_store)
    return tx

@app.delete("/transactions/{tx_id}")
def delete_transaction(tx_id: str):
    idx, _ = _find_item(_store["transactions"], tx_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    _store["transactions"].pop(idx)
    save_data(_store)
    return {"detail": "deleted"}

# ==== Budget Endpoints ==== #
@app.get("/budgets", response_model=List[Budget])
def get_budgets():
    return _store["budgets"]

@app.post("/budgets", response_model=Budget)
def create_budget(budget: Budget):
    # Simple duplicate guard
    for b in _store["budgets"]:
        if b["category"] == budget.category and b["monthYear"] == budget.monthYear:
            raise HTTPException(status_code=400, detail="Budget for this category/month already exists")
    _store["budgets"].append(budget.dict())
    save_data(_store)
    return budget

@app.put("/budgets/{budget_id}", response_model=Budget)
def update_budget(budget_id: str, budget: Budget):
    idx, _ = _find_item(_store["budgets"], budget_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    _store["budgets"][idx] = budget.dict()
    save_data(_store)
    return budget

@app.delete("/budgets/{budget_id}")
def delete_budget(budget_id: str):
    idx, _ = _find_item(_store["budgets"], budget_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    _store["budgets"].pop(idx)
    save_data(_store)
    return {"detail": "deleted"}

# ==== Goal Endpoints ==== #
@app.get("/goals", response_model=List[Goal])
def get_goals():
    return _store["goals"]

@app.post("/goals", response_model=Goal)
def create_goal(goal: Goal):
    _store["goals"].append(goal.dict())
    save_data(_store)
    return goal

@app.put("/goals/{goal_id}", response_model=Goal)
def update_goal(goal_id: str, goal: Goal):
    idx, _ = _find_item(_store["goals"], goal_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    _store["goals"][idx] = goal.dict()
    save_data(_store)
    return goal

@app.delete("/goals/{goal_id}")
def delete_goal(goal_id: str):
    idx, _ = _find_item(_store["goals"], goal_id)
    if idx is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    _store["goals"].pop(idx)
    save_data(_store)
    return {"detail": "deleted"}

# ==== Health / Info ==== #
@app.get("/health")
def health_check():
    return {"status": "ok", "provider": settings.PROVIDER}
