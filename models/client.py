from sqlalchemy import Integer, String, Column, Date, ForeignKey
from sqlalchemy.orm import relationship

from db import Base
from models.vendor_client import vendor_client


class Client(Base):
    __tablename__ = "client_table"

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, index = True, nullable = False)
    dob = Column(Date, nullable = True)
    email = Column(String, index = True, unique = True, nullable = False)
    anniversary = Column(Date , nullable = True)
    mobile = Column(String, unique = True)
    occupation = Column(String)
    address_of_property = Column(String)
    project_value = Column(Integer)
    location = Column(String)
    type_of_property = Column(String)
    billing_address = Column(String)
    sales_branch_manager = Column(String)
    designer = Column(String)

    # sales_branch_manager_id = Column(Integer, ForeignKey("users_table.id"), nullable = False)
    # designer_id = Column(Integer, ForeignKey("users_table.id"), nullable = False)
    #
    # sales_managers_fk = relationship(
    #     "User",
    #     foreign_keys=[sales_branch_manager_id],
    #     back_populates="clients_sales_manager"
    # )
    #
    # designer_fk = relationship(
    #     "User",
    #     foreign_keys=[designer_id],
    #     back_populates="clients_designer"
    # )

    vendors = relationship(
        "Vendor",
        secondary = vendor_client,
        back_populates = "clients"
    )

