import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, sessionmaker
from create_tables import create_tables
from create_db import create_db
import os
from dotenv import load_dotenv
from sqlalchemy import inspect



load_dotenv()

USER = os.getenv('USER_DB')
PASSWORD = os.getenv('PASSWORD_DB')

create_db(USER, PASSWORD)

Base = declarative_base()

DSN = 'postgresql://postgres:McDonalds106@localhost:5432/vkinder_db_1'

engine = sq.create_engine(DSN)

insp = inspect(engine)
tables = insp.get_table_names()
if 'user' and 'favorites' and 'black_list' not in tables:

    create_tables(engine)

Session = sessionmaker(bind = engine)

session = Session()






session.close()