from pathlib import Path
from typing import List, Optional

from sqlalchemy import Column, Float, ForeignKeyConstraint, Integer
from sqlmodel import Field, Relationship, SQLModel, Session, create_engine


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "baseball.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, echo=False)


def get_session() -> Session:
	"""Return a SQLModel session connected to baseball.db."""
	return Session(engine)


class People(SQLModel, table=True):
	__tablename__ = "people"

	ID: Optional[int] = None
	playerID: str = Field(primary_key=True)
	birthYear: Optional[int] = None
	birthMonth: Optional[int] = None
	birthDay: Optional[int] = None
	birthCity: Optional[str] = None
	birthCountry: Optional[str] = None
	birthState: Optional[str] = None
	deathYear: Optional[int] = None
	deathMonth: Optional[int] = None
	deathDay: Optional[int] = None
	deathCountry: Optional[str] = None
	deathState: Optional[str] = None
	deathCity: Optional[str] = None
	nameFirst: Optional[str] = None
	nameLast: Optional[str] = None
	nameGiven: Optional[str] = None
	weight: Optional[int] = None
	height: Optional[int] = None
	bats: Optional[str] = None
	throws: Optional[str] = None
	debut: Optional[str] = None
	bbrefID: Optional[str] = None
	finalGame: Optional[str] = None
	retroID: Optional[str] = None

	batting_rows: List["Batting"] = Relationship(back_populates="player")


class Teams(SQLModel, table=True):
	__tablename__ = "teams"

	yearID: int = Field(primary_key=True)
	lgID: Optional[str] = None
	teamID: str = Field(primary_key=True)
	franchID: Optional[str] = None
	divID: Optional[str] = None
	Rank: Optional[int] = None
	G: Optional[int] = None
	Ghome: Optional[int] = None
	W: Optional[int] = None
	L: Optional[int] = None
	DivWin: Optional[str] = None
	WCWin: Optional[str] = None
	LgWin: Optional[str] = None
	WSWin: Optional[str] = None
	R: Optional[int] = None
	AB: Optional[int] = None
	H: Optional[int] = None
	doubles: Optional[int] = Field(default=None, sa_column=Column("2B", Integer, nullable=True))
	triples: Optional[int] = Field(default=None, sa_column=Column("3B", Integer, nullable=True))
	HR: Optional[int] = None
	BB: Optional[int] = None
	SO: Optional[int] = None
	SB: Optional[int] = None
	CS: Optional[int] = None
	HBP: Optional[int] = None
	SF: Optional[int] = None
	RA: Optional[int] = None
	ER: Optional[int] = None
	ERA: Optional[float] = Field(default=None, sa_column=Column("ERA", Float, nullable=True))
	CG: Optional[int] = None
	SHO: Optional[int] = None
	SV: Optional[int] = None
	IPouts: Optional[int] = None
	HA: Optional[int] = None
	HRA: Optional[int] = None
	BBA: Optional[int] = None
	SOA: Optional[int] = None
	E: Optional[int] = None
	DP: Optional[int] = None
	FP: Optional[float] = Field(default=None, sa_column=Column("FP", Float, nullable=True))
	name: Optional[str] = None
	park: Optional[str] = None
	attendance: Optional[int] = None
	BPF: Optional[int] = None
	PPF: Optional[int] = None
	teamIDBR: Optional[str] = None
	teamIDlahman45: Optional[str] = None
	teamIDretro: Optional[str] = None

	batting_rows: List["Batting"] = Relationship(
		back_populates="team",
		sa_relationship_kwargs={
			"primaryjoin": "and_(Teams.teamID==foreign(Batting.teamID), Teams.yearID==foreign(Batting.yearID))"
		},
	)


class Batting(SQLModel, table=True):
	__tablename__ = "batting"
	__table_args__ = (
		ForeignKeyConstraint(["playerID"], ["people.playerID"]),
		ForeignKeyConstraint(["teamID", "yearID"], ["teams.teamID", "teams.yearID"]),
	)

	playerID: str = Field(primary_key=True)
	yearID: int = Field(primary_key=True)
	stint: int = Field(primary_key=True)
	teamID: str
	lgID: Optional[str] = None
	G: Optional[int] = None
	AB: Optional[int] = None
	R: Optional[int] = None
	H: Optional[int] = None
	doubles: Optional[int] = Field(default=None, sa_column=Column("2B", Integer, nullable=True))
	triples: Optional[int] = Field(default=None, sa_column=Column("3B", Integer, nullable=True))
	HR: Optional[int] = None
	RBI: Optional[int] = None
	SB: Optional[int] = None
	CS: Optional[int] = None
	BB: Optional[int] = None
	SO: Optional[int] = None
	IBB: Optional[int] = None
	HBP: Optional[int] = None
	SH: Optional[int] = None
	SF: Optional[int] = None
	GIDP: Optional[int] = None

	player: Optional[People] = Relationship(back_populates="batting_rows")
	team: Optional[Teams] = Relationship(
		back_populates="batting_rows",
		sa_relationship_kwargs={
			"primaryjoin": "and_(foreign(Batting.teamID)==Teams.teamID, foreign(Batting.yearID)==Teams.yearID)"
		},
	)
