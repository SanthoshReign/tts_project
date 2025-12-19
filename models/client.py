from sqlalchemy import Integer, String, Column, Date, ForeignKey
from sqlalchemy.orm import relationship

from db import Base

class Client(Base):
    __tablename__ = "client_table"

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String(100), index = True, nullable = False)
    dob = Column(Date, nullable = True)
    email = Column(String(100), index = True, unique = True, nullable = False)
    anniversary = Column(Date , nullable = True)
    mobile = Column(String(30), unique = True)
    occupation = Column(String(50))
    address_of_property = Column(String(150))
    project_value = Column(Integer)
    location = Column(String(50))
    type_of_property = Column(String(60))
    billing_address = Column(String(150))
    sales_branch_manager_id = Column(Integer, ForeignKey("users_table.id"), nullable = False)
    designer_id = Column(Integer, ForeignKey("users_table.id"), nullable = False)

    sales_managers_fk = relationship(
        "User",
        foreign_keys=[sales_branch_manager_id],
        back_populates="clients_sales_manager"
    )

    designer_fk = relationship(
        "User",
        foreign_keys=[designer_id],
        back_populates="clients_designer"
    )

