from fastapi import APIRouter
from typing import List

router = APIRouter()

@router.get("/cuisines")
async def get_cuisines() -> List[str]:
    """Get list of available cuisine types"""
    return [
        "South Asian",
        "East Asian",
        "Mediterranean",
        "Middle Eastern",
        "Latin American",
        "African",
        "Western Comfort",
        "Fusion"
    ]

@router.get("/dietary-options")
async def get_dietary_options() -> List[str]:
    """Get list of available dietary options"""
    return [
        "Vegan",
        "Vegetarian",
        "Gluten-Free",
        "High-Protein",
        "Low-Carb",
        "Comfort Food",
        "Gut-Soothing"
    ]
