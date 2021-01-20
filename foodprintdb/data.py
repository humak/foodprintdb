import psycopg2
import psycopg2.extras


class Database:

    def __init__(self, dbname='foodprintdb', user='postgres', host='localhost', password='0707'):
        self.con = psycopg2.connect(database=dbname, user=user, password=password, host=host)
        self.cur = self.con.cursor()

    def add_user(self, user):
        with self.con as conn:
            cursor = conn.cursor()
            query = "INSERT INTO users (name, username, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (user.name, user.username, user.password))
            conn.commit()

    def get_user(self, username=None, id=None):
        if id is not None:
            with self.con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                query = "SELECT * FROM users WHERE id = %s"
                cursor.execute(query, [id])
                result = cursor.fetchone()
            return result
        else:
            with self.con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                query = "SELECT * FROM users WHERE username = %s"
                cursor.execute(query, [username])
                result = cursor.fetchone()
            return result

    def delete_user(self, id):
        with self.con as conn:
            cursor = conn.cursor()
            records = self.get_records(id) 
            for record in records:
                self.delete_record(record['id']) 
            query = "DELETE from users WHERE id=%s"
            cursor.execute(query, [id])
            conn.commit()

    def get_consumptions(self, recordid):
        with self.con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = "SELECT * FROM consumptions WHERE consumptionid= %s"
            cursor.execute(query, [recordid])
            consumptions = cursor.fetchall()

            query2 = "SELECT * FROM results JOIN consumptions ON consumptions.consumptionid = %s  WHERE  consumptions.id = results.consid "
            cursor.execute(query2, [recordid])
            results = cursor.fetchall()
            print(results)
        return consumptions, results

    def get_record(self, id): 
        if not str(id).isdigit():
            return None
        with self.con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = "SELECT * FROM records WHERE id = %s"
            cursor.execute(query, [id])
            record = cursor.fetchone()
        return record

    def get_records(self, userid): 
        with self.con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = "SELECT * FROM records WHERE userid = %s"
            cursor.execute(query, [userid])
            records = cursor.fetchall()
        return records   

    def get_public_records(self):
        with self.con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = "SELECT * FROM records WHERE (isprivate = 0) ORDER BY id DESC LIMIT 10"
            cursor.execute(query)
            records = cursor.fetchall()
        return records

    def create_record(self, title, comment, userid, isprivate):
        with self.con as conn:
            cursor = conn.cursor()
            query = "INSERT INTO records(title, comment, userid, isprivate) VALUES(%s, %s, %s, %s) RETURNING id"
            cursor.execute(query, (title, comment, userid, isprivate))
            query2 = "UPDATE users SET totalrecords =totalrecords+1 WHERE id=%s"
            cursor.execute(query2, [userid])
            conn.commit()

    def update_record(self, recordid, title, comment, isprivate):
        with self.con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = 'UPDATE records SET title=%s, comment=%s, isprivate=%s WHERE id = %s'
            cursor.execute(query, (title, comment, isprivate, recordid))
            self.con.commit()

    def update_user(self, id, name=None, password=None):
        with self.con.cursor() as cursor:
            if name is not None:
                    query = "UPDATE users SET name=%s WHERE id=%s"
                    cursor.execute(query, (name, id))
            if password is not None:
                    query = "UPDATE users SET password=%s WHERE id=%s"
                    cursor.execute(query, (password, id))
            self.con.commit()

    def delete_consumption(self, consumption_id, recordid):
        with self.con as conn:
            cursor = conn.cursor()
            query = "DELETE FROM consumptions WHERE id = %s"
            cursor.execute(query, [consumption_id])
            query2 = "UPDATE records set consumptionnum = consumptionnum - 1 WHERE id = %s"
            cursor.execute(query2, [recordid])
            conn.commit()

    def delete_record(self, recordid): 
        with self.con as conn:
            cursor = conn.cursor()
            delete_consumptions = "DELETE FROM consumptions WHERE consumptionid = %s" 
            cursor.execute(delete_consumptions, [recordid])
            delete_record = "DELETE FROM records where id = %s"
            cursor.execute(delete_record, [recordid])
            get_userid = "SELECT userid FROM records WHERE id=%s"
            cursor.execute(get_userid, [recordid])
            userid = cursor.fetchone()
            query2 = "UPDATE users SET totalrecords =totalrecords t-1 WHERE id = %s"
            cursor.execute(query2, [userid])
            conn.commit()

    def add_consumption(self, title, meattype, portion, amount, consumptionid):
        with self.con as conn:
            cursor = conn.cursor()
            query = "INSERT INTO consumptions(title, meattype, portion, amount, consumptionid) VALUES(%s, %s, %s, %s, %s) RETURNING id"
            cursor.execute(query, (title, meattype, portion, amount, consumptionid))
            id_of_new_row = cursor.fetchone()[0]
            query2 = "UPDATE records set consumptionnum  = consumptionnum  + 1 WHERE id = %s"
            cursor.execute(query2, [consumptionid])
            x = int(portion)*int(amount)
            if(meattype == "beef"):
                water = (x*111)/85
                co2 = (x*0.6)/85
                land = (x* 2.4)/85
            elif(meattype == "lamb"):
                water = (x*75)/85
                co2 = (x*0.2)/85
                land = (x* 2.7)/85
            elif(meattype == "chicken"):
                water = (x*31)/85
                co2 = (x*0.1)/85
                land = (x* 0.1)/85
            elif(meattype == "pork"):
                water = (x*43)/85
                co2 = (x*0.1)/85
                land = (x* 0.1)/85
            else:
                water = -1
                co2= -1
                land= -1
            query3 = "INSERT INTO results( consid, co2_usage, water_usage , land_usage) VALUES(%s, %s, %s, %s)"
            cursor.execute(query3, ( id_of_new_row, co2, water , land))
            conn.commit()

    def get_consumption(self, consumptionid):
        if not str(consumptionid).isdigit():
            return None
        with self.con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = 'SELECT * FROM consumptions WHERE id = %s'
            cursor.execute(query, [consumptionid])
            consumption = cursor.fetchone()
        return consumption

    def update_consumption(self, title, meattype, portion, amount, consumptionid):
        with self.con as conn:
            cursor = conn.cursor()
            query = 'UPDATE consumptions SET title=%s, meattype=%s, portion=%s, amount=%s WHERE id=%s'
            cursor.execute(query, (title, meattype, portion , amount, consumptionid))
            conn.commit()

    def total_consumption(self, userid):
        with self.con as conn:
            cursor = conn.cursor()
            query = 'SELECT sum(consumptionnum) FROM records WHERE userid=%s'
            cursor.execute(query, [userid])
            result = cursor.fetchone()
            query2 = "UPDATE users SET totalcons =%s WHERE id=%s"
            cursor.execute(query2, [result, userid])
            conn.commit()
        return result


