from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from sqlmodel import Session, select
from models import engine, Batting, People, Teams

app = FastAPI()

@app.get("/years")
async def get_years():
    with Session(engine) as session:
        years = session.exec(select(Teams.yearID).distinct().order_by(Teams.yearID)).all()
    return years

@app.get("/teams")
async def get_teams(year: int):
    with Session(engine) as session:
        teams = session.exec(
            select(Teams.teamID, Teams.name, Teams.lgID, Teams.divID)
            .where(Teams.yearID == year)
            .order_by(Teams.name)
        ).all()
    return [
        {"team_id": team_id, "name": name, "league": lg, "division": div}
        for team_id, name, lg, div in teams
    ]

@app.get("/roster")
async def get_players(year: int, team_id: str):
    with Session(engine) as session:
        players = session.exec(
            select(People.nameFirst, People.nameLast)
            .join(Batting, People.playerID == Batting.playerID)
            .where((Batting.yearID == year) & (Batting.teamID == team_id))
            .distinct()
            .order_by(People.nameLast, People.nameFirst)
        ).all()
    return [{"first_name": first, "last_name": last} for first, last in players]

app.mount("/", StaticFiles(directory="static", html=True), name="static")