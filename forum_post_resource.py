import pymysql
from datetime import datetime
import os


class ForumPostResource:

    def __int__(self):
        pass

    @staticmethod
    def _get_connection():

        usr = os.environ.get("DBUSER")
        pw = os.environ.get("DBPW")
        h = os.environ.get("DBHOST")

        conn = pymysql.connect(
            user=usr,
            password=pw,
            host=h,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn

    @staticmethod
    def get_all_posts(user_id):
        sql = "SELECT P.Post_id, P.Title, P.Author, P.`Time`, L.name AS Location, " \
              " P.Label, count(T.PT_id) AS thumbs, if(U.PT_ID is null, false, true) AS is_thumbed " \
              "FROM ms3.Post P " \
              " LEFT JOIN ms3.Location L ON P.Location_ID = L.Location_ID " \
              " LEFT JOIN ms3.Post_Thumbs T ON P.Post_id = T.Post_id " \
              " LEFT JOIN (SELECT * FROM ms3.Post_Thumbs WHERE User_ID= %s) U ON P.Post_ID = U.Post_ID " \
              "GROUP BY Post_id, Title, Author, `Time`, Location, Label"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, user_id)
            # if success
            res = cur.fetchall()
            if res:
                result = {'success':True, 'data':res}
            else:
                result = {'success':False, 'message':'Not Found','data':res}
        except pymysql.Error as e:
            print(e)
            result = {'success':False, 'message':str(e)}
        return result

    def get_by_label(user_id, label):
        ## return posts
        sql1 = """
            SELECT P.Post_ID, P.Title, P.Author, P.Time, L.name AS Location, P.Label, P.Content, count(T.PT_ID) AS Thumbs, 
                if(U.Post_ID is null, false, true) AS is_Thumbed
            FROM ms3.Post P
                LEFT JOIN ms3.Location L ON P.Location_ID = L.Location_ID
                LEFT JOIN ms3.Post_Thumbs T ON P.Post_id = T.Post_id
                LEFT JOIN (
                    SELECT Post_ID
                    FROM ms3.Post_Thumbs
                    WHERE User_ID = %s
                ) U ON P.Post_ID = U.Post_ID
            WHERE P.Label = %s
            GROUP BY P.Post_id;
        """
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql1, args=(user_id, label))
            # if success
            res = cur.fetchall()
            if res:
                post = {'success': True, 'data': res}
            else:
                post = {'success': False, 'message': 'Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            post = {'success': False, 'message': str(e)}

        ## return responses
        sql2 = """
            SELECT R.Response_ID, R.Post_ID, R.Author, R.Time, R.Content, count(T.RT_ID) AS Thumbs, 
                if(U.Response_ID is null, false, true) AS is_Thumbed, if(L.Post_ID is null, false, true) AS correct_Label
            FROM ms3.Response R
                LEFT JOIN ms3.Response_Thumbs T ON R.Response_ID = T.Response_ID
                LEFT JOIN (
                    SELECT Response_ID, User_ID
                    FROM ms3.Response_Thumbs
                    WHERE User_ID = %s
                ) U ON R.Response_ID = U.Response_ID
                LEFT JOIN (
                    SELECT Post_ID, Label
                    FROM ms3.Post
                    WHERE Label = %s
                ) L ON R.Post_ID = L.Post_ID
            GROUP BY R.Response_ID
            HAVING correct_Label = TRUE;
        """
        cur = conn.cursor()
        try:
            cur.execute(sql2, args=(user_id, label))
            # if success
            res = cur.fetchall()
            if res:
                response = {'success': True, 'data': res}
            else:
                response = {'success': False, 'message': 'Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            response = {'success': False, 'message': str(e)}
        return {"post": post, "response": response}

    def get_by_id(user_id, post_id):

        conn = ForumPostResource._get_connection()

        ## return post details
        sql1 = """
            SELECT P.* , count(T.PT_id) AS thumbs, if(U.PT_ID is null, false, true) AS is_thumbed
            FROM ms3.Post P
                LEFT JOIN ms3.Post_Thumbs T ON P.Post_id = T.Post_id
                LEFT JOIN (SELECT * FROM ms3.Post_Thumbs WHERE User_ID= %s) U ON P.Post_ID = U.Post_ID
            WHERE P.Post_ID = %s
            GROUP BY P.Post_ID;
            """
        cur = conn.cursor()
        try:
            cur.execute(sql1, args=(user_id, post_id))
            # if success
            res = cur.fetchall()
            if res:
                post = {'success': True, 'data': res}
            else:
                post = {'success': False, 'message': 'Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            post = {'success': False, 'message': str(e)}

        ## return responses
        sql2 = """
            SELECT R.*, count(T.RT_ID) AS thumbs, if(U.RT_ID is null, false, true) AS is_thumbed
            FROM ms3.Response R LEFT JOIN ms3.Response_Thumbs T
                ON R.Response_ID = T.Response_ID
                LEFT JOIN (SELECT * FROM ms3.Response_Thumbs WHERE User_ID= %s) U ON R.Response_ID = U.Response_ID
            WHERE R.Post_ID = %s
            GROUP BY R.Response_ID;
        """
        cur = conn.cursor()
        try:
            cur.execute(sql2, args=(user_id, post_id))
            # if success
            res = cur.fetchall()
            if res:
                response = {'success': True, 'data': res}
            else:
                response = {'success': False, 'message': 'Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            response = {'success': False, 'message': str(e)}
            return response

        return {"post": post, "response": response}

    def add_post(user_id, title, location, label, content):
        t = str(datetime.now())
        sql = "INSERT INTO ms3.Post (Title, Author, Time, Location_ID, Label, Content) VALUES (%s,%s,%s,%s,%s,%s)"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args=(title, user_id, t, location, label, content))
            res = cur.fetchall()
            if res:
                result = {'success': True, 'data': res}
            else:
                result = {'success': False, 'message': 'Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def add_response(user_id, post_id, content):
        t = str(datetime.now())
        sql = "INSERT INTO ms3.Response (Post_ID, Author, Time, Content) VALUES (%s,%s,%s,%s)"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, args=(post_id, user_id, t, content))
            res = cur.fetchall()
            if res:
                result = {'success': True, 'data': res}
            else:
                result = {'success': False, 'message': 'Not Found', 'data': res}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def click_thumb_post(post_id, user_id):
        sql_p = "SELECT * FROM ms3.Post_Thumbs WHERE Post_ID = %s AND User_ID = %s;"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql_p, args=(post_id, user_id))
            res = cur.fetchall()
            # if already thumbed
            if res:
                sql = "DELETE FROM ms3.Post_Thumbs WHERE Post_ID = %s AND User_ID = %s;"
                cur.execute(sql, args=(post_id, user_id))
                result = {'success': True, 'message': 'Thumb deleted to post'}
            else:
                sql = "INSERT INTO ms3.Post_Thumbs VALUES (DEFAULT,%s,%s)"
                cur.execute(sql, args=(post_id, user_id))
                result = {'success': True, 'message': 'Thumb added to post'}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def click_thumb_response(resp_id, user_id):
        sql_p = "SELECT * FROM ms3.Response_Thumbs WHERE Response_ID = %s AND User_ID = %s;"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql_p, args=(resp_id, user_id))
            res = cur.fetchall()
            # if already thumbed
            if res:
                sql = "DELETE FROM ms3.Response_Thumbs WHERE Response_ID = %s AND User_ID = %s;"
                cur.execute(sql, args=(resp_id, user_id))
                result = {'success': True, 'message': 'Thumb deleted to Response'}
            else:
                sql = "INSERT INTO ms3.Response_Thumbs VALUES (DEFAULT,%s,%s)"
                cur.execute(sql, args=(resp_id, user_id))
                result = {'success': True, 'message': 'Thumb added to Response'}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    # def get_by_key(key):
    #
    #     sql = "SELECT * FROM f22_databases.columbia_students where guid=%s";
    #     conn = ColumbiaStudentResource._get_connection()
    #     cur = conn.cursor()
    #     res = cur.execute(sql, args=key)
    #     result = cur.fetchone()
    #
    #     return result

