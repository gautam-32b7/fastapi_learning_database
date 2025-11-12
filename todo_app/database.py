from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos.db'
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
#                        'check_same_thread': False})
DATABASE_URL = "mssql+pyodbc://@localhost\\SQLEXPRESS/TodosApp?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
