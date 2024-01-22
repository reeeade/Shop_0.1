from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

hostname = os.environ.get('DB_HOSTNAME', 'localhost')
db_name = os.environ.get('DB_NAME', 'postgres')
username = os.environ.get('DB_USERNAME', 'postgres')
password = os.environ.get('DB_PASSWORD', 'mypassword')
port = os.environ.get('DB_PORT', '5432')

engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{db_name}')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models
    Base.metadata.create_all(bind=engine)
