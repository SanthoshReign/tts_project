from sqlalchemy import Table, Column, ForeignKey, Integer
from db import Base

vendor_client = Table(
    "vendor_client",
    Base.metadata,
    Column(
        "vendor_id",
        Integer,
        ForeignKey("vendor_table.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "client_id",
        Integer,
        ForeignKey("client_table.id", ondelete="CASCADE"),
        primary_key=True
    ),
)
