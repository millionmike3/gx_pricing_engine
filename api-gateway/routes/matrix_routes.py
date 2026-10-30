from fastapi import APIRouter

router = APIRouter()

@router.get("/grid")
def get_matrix():
    return {"matrix": "pricing grid goes here"}
