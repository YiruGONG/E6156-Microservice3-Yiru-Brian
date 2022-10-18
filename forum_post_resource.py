import pymysql

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
    def get_all_posts():
        sql = "SELECT P.Post_id, P.Title, P.Author, P.`Time`, L.name AS Location, P.Label, count(T.PT_id) AS thumbs " \
              "FROM ms3.Post P " \
              "LEFT JOIN ms3.Location L ON P.Location_ID = L.Location_ID " \
              "LEFT JOIN ms3.Post_Thumbs T ON P.Post_id = T.Post_id " \
              "GROUP BY P.Post_id, P.Title, P.Author, P.`Time`, Location, P.Label "
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql)
        result = cur.fetchall()
        return result

    # def get_by_label(label):
    #     ## TO DO...

    def get_by_id(post_id):
        conn = ForumPostResource._get_connection()
        sql1 = "SELECT * " \
               "FROM ms3.Post P LEFT JOIN ms3.Post_Thumbs T " \
               "    ON P.Post_id = T.Post_id" \
               "WHERE Post_ID = :post_id"
        post = conn.cursor().execute(sql1, post_id=post_id).fetchall()

        sql2 = "SELECT * FROM ms3.Response WHERE Post_ID = :post_id"
        response = conn.cursor().execute(sql2).fetchall()

        return list(post = post,
                    response = response)


    # def get_by_key(key):
    #
    #     sql = "SELECT * FROM f22_databases.columbia_students where guid=%s";
    #     conn = ColumbiaStudentResource._get_connection()
    #     cur = conn.cursor()
    #     res = cur.execute(sql, args=key)
    #     result = cur.fetchone()
    #
    #     return result

