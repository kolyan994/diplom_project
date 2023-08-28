import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect


Base = declarative_base()

class ModelProcessor:
    def __init__(self, user, password):
        create_db(user, password)
        dns = f'postgresql://{user}:{password}@localhost:5432/vkinder_db'
        engine = sq.create_engine(dns)

        insp = inspect(engine)
        tables = insp.get_table_names()
        if 'user' and 'favorites' and 'black_list' not in tables:
            create_tables(engine)

        self.Session = sessionmaker(bind = engine)

    def user_update(self, user):
        with self.Session() as s:
            s.add(user)
            s.commit()

    def user_add(self, user_id):
        with self.Session() as s:
            user = s.query(User).get(user_id)
            if user is None:
                user = User(
                    id = user_id,
                    offset = 0,
                    page = 'main',
                    last_person = 0)
                s.add(user)
                s.flush()
                s.refresh(user)
                s.commit()
        return user

    def blacklist_add(self, user_id):
        with self.Session() as s:
            user = s.query(User).get(user_id)
            fav_list = s.query(Favourites.person_id).filter(Favourites.user_id == user_id)
            if user.last_person in fav_list:
                s.delete(Favourites).filter(Favourites.person_id == user.last_person)
            black_list = BlackList(
                user = user,
                person_id = user.last_person
            )
            s.add(black_list)
            s.commit()

    def favourites_add(self, user_id):
        with self.Session() as s:
            user = s.query(User).get(user_id)
            favourites = Favourites(
                user = user,
                person_id = user.last_person
            )
            s.add(favourites)
            s.commit()

    def favourites_get(self, user_id):
        with self.Session() as s:
            fav_list = s.query(Favourites.person_id).filter(Favourites.user_id == user_id).all()
            fav_list = [person[0] for person in fav_list]
            return fav_list
        
    def favourites_delete(self, user_id, delete_id):
        with self.Session() as s:
            fav = s.query(Favourites).filter_by(user_id=user_id, person_id=delete_id).first()
            s.delete(fav)
            s.commit()


class User(Base):
    __tablename__ = "user"
    
    id = sq.Column(sq.Integer, primary_key=True)
    last_person = sq.Column(sq.Integer)
    offset = sq.Column(sq.Integer)
    page = sq.Column(sq.String(length=6))


class Favourites(Base):
    __tablename__ = "favourites"

    user_id = sq.Column(sq.Integer(), sq.ForeignKey('user.id'), primary_key=True)
    person_id = sq.Column(sq.Integer, primary_key=True)

    user = relationship(User, backref='favourites')


class BlackList(Base):
    __tablename__ = "blacklist"

    user_id = sq.Column(sq.Integer(), sq.ForeignKey('user.id'), primary_key=True)
    person_id = sq.Column(sq.Integer, primary_key=True)

    user = relationship(User, backref='blacklist')


def create_tables(engine):
    Base.metadata.create_all(engine)


def create_db(USER, PASSWORD):
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host="localhost",
            port="5432")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()
        sql_create_database = 'create database vkinder_db'
        cursor.execute(sql_create_database)
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            # print("Соединение с PostgreSQL закрыто")
