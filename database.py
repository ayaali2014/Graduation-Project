from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLELCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/gp"

engine = create_engine(SQLELCHEMY_DATABASE_URL)

Sessionlocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base() 