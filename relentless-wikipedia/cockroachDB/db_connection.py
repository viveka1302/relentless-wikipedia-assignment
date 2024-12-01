import os
from sqlalchemy import create_engine, text
from wikipedia_settings.settings import settings as set
from sqlalchemy import Table, MetaData, update, delete


engine = create_engine(os.environ["DATABASE_URL"])
conn = engine.connect()

metadata = MetaData()
users_table = Table(
    'userdata', metadata,
    autoload_with=engine  
)
sr_table= Table(
    "searchresults", metadata, autoload_with=engine
)
saved_article_table= Table(
    "savedarticles", metadata, autoload_with=engine
    )

res = conn.execute(text("SELECT now()")).fetchall()
print(res)