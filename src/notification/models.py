from src.app.database import Base

from sqlalchemy import Column, Integer, JSON
from sqlalchemy.orm import Session


class NoticationConnections(Base):
    __tablename__ = "websocket_connections"
    id = Column(Integer, primary_key=True, nullable=False)
    wsock = Column(JSON, nullable=False)
    user_id = Column(Integer, nullable=False, unique=True)


class Repo:
    def __init__(self, db: Session):
        self.db = db

    @property
    def base(self):
        return self.db.query(NoticationConnections)

    def get_connections(self):
        return self.base.all()

    def get_wsock(self, user_id: int):
        return self.base.filter(NoticationConnections.user_id == user_id).first()

    def create(self, user_id: int, wsock: dict) -> NoticationConnections:
        wbsock = NoticationConnections(user_id=user_id, wsock=wsock)
        self.db.add(wbsock)
        self.db.commit()

    def delete(self, user_id: int):
        wbsock = self.get_wsock(user_id)
        if wbsock:
            self.db.delete(wbsock)
            self.db.commit()
