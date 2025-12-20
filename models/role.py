from sqlalchemy import Column, Integer, String

from db import Base

class Role(Base):
    __tablename__ = "role_table"

    id = Column(Integer, primary_key = True)
    role_name = Column(String, unique = True, nullable = False)
    permission = Column(String, nullable = False)