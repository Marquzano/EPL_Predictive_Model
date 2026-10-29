from fastapi import APIRouter, Depends
from typing import Annotated
import sqlite3
from app.api.dependencies import get_con
from app.services.teams import get_teams
from app.schemas.schemas import TeamResponse

router = APIRouter()

# make the route to get teams for the frontend
@router.get('/teams', response_model=list[TeamResponse])
def teams(con: Annotated[sqlite3.Connection, Depends(get_con)]):
    result = get_teams(con)

    return result