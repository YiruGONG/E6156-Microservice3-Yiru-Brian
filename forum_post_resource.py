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
        sql = """
            SELECT P.Post_ID, P.Title, P.User_ID, P.Time, L.Name AS Location, L.Map_URL, P.Label, count(T.PT_id) AS Thumbs, if(U.PT_ID is null, false, true) AS is_Thumbed
            FROM ms3.Post P
            LEFT JOIN ms3.Location L ON P.Location_ID = L.Location_ID
            LEFT JOIN ms3.Post_Thumbs T ON P.Post_id = T.Post_id
            LEFT JOIN (SELECT * FROM ms3.Post_Thumbs WHERE User_ID= %s) U ON P.Post_ID = U.Post_ID
            GROUP BY Post_id, Title, User_ID, Time, Location, Label;
        """
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, user_id)
            # if success
            res = cur.fetchall()
            if res:
                label = list(set([x['Label'] for x in res]))
                label = [i for i in label if i is not None]
                result = {'success': True, 'data': res, 'labels': label}
            else:
                result = {'success':False, 'message':'Not Found','data':res}
        except pymysql.Error as e:
            print(e)
            result = {'success':False, 'message':str(e)}
        return result

    def get_posts_by_label(user_id, label):
        ## return posts
        sql1 = """
            SELECT P.Post_ID, P.Title, P.User_ID, P.Time, L.Name AS Location, P.Label, count(T.PT_ID) AS Thumbs, 
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
            cur.execute(sql1 % (user_id, label))
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
            SELECT R.Response_ID, R.Post_ID, R.User_ID, R.Time, R.Content, count(T.RT_ID) AS Thumbs, 
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
            cur.execute(sql2 % (user_id, label))
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

    def get_posts_by_id(user_id, post_id):

        conn = ForumPostResource._get_connection()

        ## return post details
        sql1 = """
            SELECT P.* , L.Name AS Location, L.Map_URL, count(T.PT_id) AS Thumbs, if(U.PT_ID is null, false, true) AS is_Thumbed
            FROM ms3.Post P
                LEFT JOIN ms3.Post_Thumbs T ON P.Post_id = T.Post_id
                LEFT JOIN (SELECT * FROM ms3.Post_Thumbs WHERE User_ID= %s) U ON P.Post_ID = U.Post_ID
            WHERE P.Post_ID = %s
            GROUP BY P.Post_ID;
            """
        cur = conn.cursor()
        try:
            cur.execute(sql1 % (user_id, post_id))
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
            SELECT R.*, count(T.RT_ID) AS Thumbs, if(U.RT_ID is null, false, true) AS is_Thumbed
            FROM ms3.Response R LEFT JOIN ms3.Response_Thumbs T
                ON R.Response_ID = T.Response_ID
                LEFT JOIN (SELECT * FROM ms3.Response_Thumbs WHERE User_ID= %s) U ON R.Response_ID = U.Response_ID
            WHERE R.Post_ID = %s
            GROUP BY R.Response_ID;
        """
        cur = conn.cursor()
        try:
            cur.execute(sql2 % (user_id, post_id))
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

    def get_my_posts(user_id):

        conn = ForumPostResource._get_connection()

        ## return post details
        sql1 = """
            SELECT P.Post_ID, P.Title, P.User_ID, P.Time, L.Name AS Location, P.Label, count(T.PT_ID) AS Thumbs,
                if(U.Post_ID is null, false, true) AS is_Thumbed
            FROM ms3.Post P
                LEFT JOIN ms3.Location L ON P.Location_ID = L.Location_ID
                LEFT JOIN ms3.Post_Thumbs T ON P.Post_id = T.Post_id
                LEFT JOIN (
                    SELECT Post_ID
                    FROM ms3.Post_Thumbs
                    WHERE User_ID = %s
                ) U ON P.Post_ID = U.Post_ID
            WHERE P.User_ID = %s
            GROUP BY P.Post_id;
        """
        cur = conn.cursor()
        try:
            cur.execute(sql1 % (user_id, user_id))
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
            SELECT R.Response_ID, R.Post_ID, R.User_ID, R.Time, R.Content, count(T.RT_ID) AS Thumbs,
                if(U.Response_ID is null, false, true) AS is_Thumbed,  if(L.Post_ID is null, false, true) AS mypost
            FROM ms3.Response R
                LEFT JOIN ms3.Response_Thumbs T ON R.Response_ID = T.Response_ID
                LEFT JOIN (
                    SELECT Response_ID, User_ID
                    FROM ms3.Response_Thumbs
                    WHERE User_ID = %s
                ) U ON R.Response_ID = U.Response_ID
                LEFT JOIN (
                    SELECT Post_ID, User_ID
                    FROM ms3.Post
                    WHERE User_ID = %s
                ) L ON R.Post_ID = L.Post_ID
            GROUP BY R.Response_ID
            HAVING mypost = TRUE;
        """
        cur = conn.cursor()
        try:
            cur.execute(sql2 % (user_id, user_id))
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

    def add_post(user_id, title, location, label, content):
        t = str(datetime.now())
        sql_query = "SELECT COUNT(Post_ID) FROM ms3.Post;"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql_query)
            key, val1 = next(iter(cur.fetchone().items()))
            if location == 'None' and label == 'None':
                cur.execute("INSERT INTO ms3.Post (Title, User_ID, Time, Content) VALUES (\'%s\', %s, \'%s\', \'%s\';" % (title, user_id, t, content))
            elif location == 'None' and label != 'None':
                cur.execute("INSERT INTO ms3.Post (Title, User_ID, Time, Label, Content) VALUES (\'%s\', %s, \'%s\', \'%s\', \'%s\');" % (title, user_id, t, label, content))
            elif location != 'None' and label == 'None':
                cur.execute("INSERT INTO ms3.Post (Title, User_ID, Time, Location_ID, Content) VALUES (\'%s\', %s, \'%s\', %d, \'%s\');" % (title, user_id, t, int(location), content))
            else:
                cur.execute("INSERT INTO ms3.Post (Title, User_ID, Time, Location_ID, Label, Content) VALUES (\'%s\', %s, \'%s\', %d, \'%s\', \'%s\');" % (title, user_id, t, int(location), label, content))
            cur.execute(sql_query)
            key, val2 = next(iter(cur.fetchone().items()))
            if val2 - val1 == 1:
                result = {'success': True, 'message': 'post added'}
            else:
                result = {'success': False, 'message': 'post not added'}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def add_response(user_id, post_id, content):
        t = str(datetime.now())
        sql_query_post = "SELECT Title FROM ms3.Post WHERE Post_ID = %s;"
        sql_query_resp = "SELECT COUNT(Response_ID) FROM ms3.Response WHERE Post_ID = %s;"
        sql_insert = "INSERT INTO ms3.Response (Post_ID, User_ID, Time, Content) VALUES (%s, %s, \'%s\', \'%s\');"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()

        try:
            cur.execute(sql_query_post % post_id)
            res = cur.fetchall()
            if res:
                post_result = {'success': True, 'message': 'post found'}
            else:
                post_result = {'success': False, 'message': 'post not found, cannot add response'}
        except pymysql.Error as e:
            print(e)
            post_result = {'success': False, 'message': str(e)}

        try:
            cur.execute(sql_query_resp % post_id)
            key, val1 = next(iter(cur.fetchone().items()))
            cur.execute(sql_insert % (post_id, user_id, t, content))
            cur.execute(sql_query_resp % post_id)
            key, val2 = next(iter(cur.fetchone().items()))
            if val2 - val1 == 1:
                resp_result = {'success': True, 'message': 'response added to post'}
            else:
                resp_result = {'success': False, 'message': 'post found but response not added'}
        except pymysql.Error as e:
            print(e)
            resp_result = {'success': False, 'message': str(e)}

        return {'post': post_result, 'response': resp_result}

    def update_response(user_id, response_id, content):
        ori_entry = {
            "Post_ID": 5,
            "Title": "first new post via postman again",
            "User_ID": "Yiru Gong",
            "Time": "2022-10-24 16:31:45",
            "Location_ID": 2,
            "Label": "Others",
            "Content": "edit post api testing again",
            "Edited": 0,
            "Thumbs": 0,
            "is_Thumbed": 0
        }
        # ori_entry = obj.get_post_by_id(user_id, post_id)["post"]["post_data"][0]
        print("ori_entry received")
        # for item in ["Title", "Location_ID", "Label", "Content"]:
        #     print(ori_entry[item], type(ori_entry[item]))
        # print(title, type(title), location, type(location), label, type(label), content, type(content))
        if ori_entry["Title"] == title and ori_entry["Location_ID"] == int(location) and ori_entry["Label"] == label and ori_entry['Content'] == content:
            result = {'success': False, 'message': 'post unedited'}
            return result
        else:
            t = str(datetime.now())
            sql_query = "SELECT COUNT(Post_ID) FROM ms3.Post;"
            conn = ForumPostResource._get_connection()
            cur = conn.cursor()
            try:
                cur.execute(sql_query)
                key, val1 = next(iter(cur.fetchone().items()))
                cur.execute("DELETE FROM ms3.Post WHERE Post_ID = %s" % post_id)
                if location == 'None' and label == 'None':
                    cur.execute("INSERT INTO ms3.Post (Post_ID, Title, User_ID, Time, Content, Edited) VALUES (%s, \'%s\', %s, \'%s\', \'%s\', %s);" % (post_id, title, user_id, t, content, 1))
                elif location == 'None' and label != 'None':
                    cur.execute("INSERT INTO ms3.Post (Post_ID, Title, User_ID, Time, Label, Content, Edited) VALUES (%s, \'%s\', %s, \'%s\', \'%s\', \'%s\', %s);" % (post_id, title, user_id, t, label, content, 1))
                elif location != 'None' and label == 'None':
                    cur.execute("INSERT INTO ms3.Post (Post_ID, Title, User_ID, Time, Location_ID, Content, Edited) VALUES (%s, \'%s\', %s, \'%s\', \'%s\', \'%s\', %s);" % (post_id, title, user_id, t, location, content, 1))
                else:
                    cur.execute("INSERT INTO ms3.Post (Post_ID, Title, User_ID, Time, Location_ID, Label, Content, Edited) VALUES (%s, \'%s\', %s, \'%s\', \'%s\', \'%s\', \'%s\', %s);" % (post_id, title, user_id, t, location, label, content, 1))
                cur.execute(sql_query)
                key, val2 = next(iter(cur.fetchone().items()))
                if val2 == val1:
                    result = {'success': True, 'message': 'post edited'}
                else:
                    result = {'success': False, 'message': 'post not edited'}
            except pymysql.Error as e:
                print(e)
                result = {'success': False, 'message': str(e)}
            return result

    def post_delete(post_id):
        sql = "DELETE FROM ms3.Post WHERE post_id = %s"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, post_id)
            result = {'success': True, 'message': 'Post deleted successfully'}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def resp_delete(resp_id):
        sql = "DELETE FROM ms3.Response WHERE response_id = %s"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, resp_id)
            result = {'success': True, 'message': 'Response deleted successfully'}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def click_thumb_post(post_id, user_id):
        sql_p = "SELECT * FROM ms3.Post_Thumbs WHERE Post_ID = %s AND User_ID = %s;"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql_p % (post_id, user_id))
            res = cur.fetchall()
            # if already thumbed
            if res:
                sql = "DELETE FROM ms3.Post_Thumbs WHERE Post_ID = %s AND User_ID = %s;"
                cur.execute(sql % (post_id, user_id))
                result = {'success': True, 'message': 'Thumb deleted to post'}
            else:
                sql = "INSERT INTO ms3.Post_Thumbs VALUES (DEFAULT,%s,%s);"
                cur.execute(sql % (post_id, user_id))
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

