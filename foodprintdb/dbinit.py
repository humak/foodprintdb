
import os
import sys
import psycopg2 as dbapi2

INIT_STATEMENTS = [
    '''CREATE TABLE IF NOT EXISTS users(
        name varchar(25), 
        id SERIAL, 
        username varchar(25), 
        password varchar(100),
        totalrecords INTEGER DEFAULT 0, 
        totalcons INTEGER DEFAULT 0, 
        PRIMARY KEY (id)
    )''',
    '''CREATE TABLE IF NOT EXISTS records( 
        id SERIAL,
        userid INTEGER REF ERENCES users(id),
        comment text,
        create_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
        consumptionnum integer DEFAULT 0,
        isprivate integer,
        title varchar(50),
        PRIMARY KEY (id),
    )''',
    '''CREATE TABLE IF NOT EXISTS consumptions(
        id SERIAL,
        title varchar(50),
        meattype varchar(50),
        meatid INTEGER,
        amount varchar(5),
        consumptionid INTEGER REFERENCES records(id),
        portion varchar(10),
        PRIMARY KEY (id)
    )''',
    '''CREATE TABLE IF NOT EXISTS results( 
        id SERIAL,
        consid INTEGER REFERENCES consumptions(id),
        co2_usage float,
        water_usage float,
        land_usage float,
        PRIMARY KEY (id),
    )'''

]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
