from fastapi import APIRouter
import json
import os

router = APIRouter()

@router.get("/matrix/current")
def get_matrix():
    # Build path to pricing_matrix.json
    base_dir = os.path.dirname(os.path.dirname(__file__))  # backend/
    data_path = os.path.join(base_dir, "data", "pricing_matrix.json")

    with open(data_path, "r") as f:
        matrix = json.load(f)

    return matrix
