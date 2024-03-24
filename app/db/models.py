from sqlalchemy import Column, Integer, BigInteger, Numeric, String, TIMESTAMP, func

from app.db.database import Base


class DistributionEvent(Base):
    __tablename__ = "distribution_events"

    id = Column(Integer, primary_key=True)
    block_number = Column(BigInteger, nullable=False)
    transaction_index = Column(Integer, nullable=False)
    log_index = Column(Integer, nullable=False)
    input_aix_amount = Column(Numeric(50, 0), nullable=False)
    distributed_aix_amount = Column(Numeric(50, 0), nullable=False)
    swapped_eth_amount = Column(Numeric(50, 0), nullable=False)
    distributed_eth_amount = Column(Numeric(50, 0), nullable=False)
    occurred_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())
