import os
import pymysql
from datetime import datetime
from smartystreets_python_sdk import StaticCredentials, exceptions, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup as StreetLookup
import requests

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


    # def get_all_posts(user_id):
    #     sql = """
    #         SELECT P.Post_ID, P.Title, P.User_ID, P.Time, L.Name AS Location, L.Map_URL, P.Label, count(T.PT_id) AS Thumbs,
    #             if(U.PT_ID is null, false, true) AS is_Thumbed
    #         FROM ms3.Post P
    #             LEFT JOIN ms3.Location L ON P.Location_ID = L.Location_ID
    #             LEFT JOIN ms3.Post_Thumbs T ON P.Post_id = T.Post_id
    #             LEFT JOIN (
    #                 SELECT *
    #                 FROM ms3.Post_Thumbs
    #                 WHERE User_ID= %s
    #             ) U ON P.Post_ID = U.Post_ID
    #         GROUP BY Post_id, Title, User_ID, Time, Location, Label
    #         LIMIT 5;
    #     """
    #     conn = ForumPostResource._get_connection()
    #     cur = conn.cursor()
    #     try:
    #         cur.execute(sql, user_id)
    #         # if success
    #         res = cur.fetchall()
    #         if res:
    #             label = list(set([x['Label'] for x in res]))
    #             label = [i for i in label if i is not None]
    #             result = {'success': True, 'data': res, 'labels': label}
    #         else:
    #             result = {'success': False, 'message': 'Not Found', 'data': res}
    #     except pymysql.Error as e:
    #         print(e)
    #         result = {'success': False, 'message': str(e)}
    #     return result

    def get_all_posts(user_id, label = '5', sort = '1', limit = '2', page = '1', mypost = '0'):
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        sql = """
            SELECT P.Post_ID, P.Title, P.User_ID, P.Time, P.Location_ID, L.Name AS Location, L.Map_URL, P.Label, P.Content, P.Edited,
                count(T.PT_ID) AS Thumbs, if(U.Post_ID is null, false, true) AS is_Thumbed
            FROM ms3.Post P
                LEFT JOIN ms3.Location L ON P.Location_ID = L.Location_ID
                LEFT JOIN ms3.Post_Thumbs T ON P.Post_id = T.Post_id
                LEFT JOIN (
                    SELECT Post_ID
                    FROM ms3.Post_Thumbs
                    WHERE User_ID = %s
                ) U ON P.Post_ID = U.Post_ID
            GROUP BY P.Post_id
            LIMIT %s
            OFFSET %s;
        """
        limit = int(limit)
        offset = (int(page)-1)*int(limit)
        if label != '5':
            label_dict = {'1': 'Administrative', '2': 'Lost and Found', '3': 'Call for Partners', '4': 'Others'}
            label = label_dict[label]
            s_list = sql.split("GROUP BY")
            s_list.insert(1, "WHERE P.Label = %s GROUP BY")
            sql = ''.join(s_list)
        if mypost == '1':
            s_list = sql.split("GROUP BY")
            s_list.insert(1, "WHERE P.User_ID = %s GROUP BY")
            sql = ''.join(s_list)
        if sort == '3':
            ## return recent posts that are relatively popular
            t = str(datetime.now())
            s_list = sql.split("GROUP BY")
            s_list.insert(1, "WHERE DATEDIFF(%s, P.Time) < 100 GROUP BY")
            sql = ''.join(s_list)
            s_list = sql.split("LIMIT")
            res_count_sql = "SELECT COUNT(C.Post_ID) AS Post_count FROM ({}) C;".format(s_list[0])
            s_list.insert(1, "ORDER BY Thumbs DESC LIMIT")
            sql = ''.join(s_list)
            s_list = sql.split('WHERE')
            sql = 'WHERE'.join(s_list[0:3])
            s_list = s_list[3:]
            s_list.insert(0, sql)
            sql = ' AND '.join(s_list)
            print(sql)
            print(res_count_sql)
            try:
                if ((label != '5') & (mypost == '1')):
                    cur.execute(sql, args=(user_id, t, label, user_id, limit, offset))
                elif label != '5':
                    cur.execute(sql, args=(user_id, t, label, limit, offset))
                elif mypost == '1':
                    cur.execute(sql, args=(user_id, t, user_id, limit, offset))
                else:
                    cur.execute(sql, args=(user_id, t, limit, offset))
                res = cur.fetchall()
                if res:
                    if ((label != '5') & (mypost == '1')):
                        cur.execute(res_count_sql, args=(user_id, t, label, user_id))
                    elif label != '5':
                        cur.execute(res_count_sql, args=(user_id, t, label))
                    elif mypost == '1':
                        cur.execute(res_count_sql, args=(user_id, t, user_id))
                    else:
                        cur.execute(res_count_sql, args=(user_id, t))
                    key, count = next(iter(cur.fetchone().items()))
                    post = {'success': True, 'data': res, "count": count, "message": "Up tp 5 most popular recent (3 weeks) posts in described category"}
                else:
                    post = {'success': False, 'data': res, 'message': 'No recent posts in described category'}
            except pymysql.Error as e:
                print(e)
                post = {'success': False, 'message': str(e)}
        else:
            s_list = sql.split('WHERE')
            sql = 'WHERE'.join(s_list[0:3])
            s_list = s_list[3:]
            s_list.insert(0, sql)
            sql = ' AND '.join(s_list)
            s_list = sql.split("LIMIT")
            res_count_sql = "SELECT COUNT(C.Post_ID) AS Post_count FROM ({}) C;".format(s_list[0])
            if sort == '2':
                ## return posts that are the most popular
                s_list.insert(1, "ORDER BY Thumbs DESC LIMIT")
            else:
                ## return posts that are the most recent
                s_list.insert(1, "ORDER BY Time DESC LIMIT")
            sql = ''.join(s_list)
            print(sql)
            print(res_count_sql)
            try:
                if ((label != '5') & (mypost == '1')):
                    cur.execute(sql, args=(user_id, label, user_id, limit, offset))
                elif label != '5':
                    cur.execute(sql, args=(user_id, label, limit, offset))
                elif mypost == '1':
                    cur.execute(sql, args=(user_id, user_id, limit, offset))
                else:
                    cur.execute(sql, args=(user_id, limit, offset))
                res = cur.fetchall()
                if res:
                    if ((label != '5') & (mypost == '1')):
                        cur.execute(res_count_sql, args=(user_id, label, user_id))
                    elif label != '5':
                        cur.execute(res_count_sql, args=(user_id, label))
                    elif mypost == '1':
                        cur.execute(res_count_sql, args=(user_id, user_id))
                    else:
                        cur.execute(res_count_sql, args=(user_id))
                    key, count = next(iter(cur.fetchone().items()))
                    if sort == '2':
                        post = {'success': True, 'data': res, "count": count, "message": "Up to 5 most popular posts in the described cateogry"}
                    else:
                        post = {'success': True, 'data': res, "count": count, "message": "Up to 5 most recent posts in the described cateogry"}
                    for apost in res:
                        userid_post = apost['User_ID']
                        user_info = requests.get(f'{os.environ.get("MS2_URL")}api/userprofile3/{userid_post}').json()['data'][0]
                        apost['profile_pic'] = user_info['profile_pic']
                        apost['username'] = user_info['username']
                else:
                    post = {'success': False, 'data': res, 'message': 'No post found in the described category'}
                

            except pymysql.Error as e:
                print(e)
                post = {'success': False, 'message': str(e)}

        return post

    # def get_posts_by_label(user_id, label):
    #     ## return posts under a subcategory
    #     sql1 = """
    #         SELECT P.Post_ID, P.Title, P.User_ID, P.Time, L.Name AS Location, L.Map_URL, P.Label, count(T.PT_ID) AS Thumbs,
    #             if(U.Post_ID is null, false, true) AS is_Thumbed, P.Edited As is_Edited
    #         FROM ms3.Post P
    #             LEFT JOIN ms3.Location L ON P.Location_ID = L.Location_ID
    #             LEFT JOIN ms3.Post_Thumbs T ON P.Post_id = T.Post_id
    #             LEFT JOIN (
    #                 SELECT Post_ID
    #                 FROM ms3.Post_Thumbs
    #                 WHERE User_ID = %s
    #             ) U ON P.Post_ID = U.Post_ID
    #         WHERE P.Label = %s
    #         GROUP BY P.Post_id
    #         LIMIT 5;
    #     """
    #     label_dict = {'1': 'Administrative', '2': 'Lost and Found', '3': 'Call for Partners', '4': 'Others'}
    #     label = label_dict[label]
    #     conn = ForumPostResource._get_connection()
    #     cur = conn.cursor()
    #     try:
    #         cur.execute(sql1, args=(user_id, label))
    #         res = cur.fetchall()
    #         if res:
    #             post = {'success': True, 'data': res}
    #         else:
    #             post = {'success': False, 'message': 'Not Found', 'data': res}
    #     except pymysql.Error as e:
    #         print(e)
    #         post = {'success': False, 'message': str(e)}
    #
    #     ## return responses
    #     # sql2 = """
    #     #     SELECT R.Response_ID, R.Post_ID, R.User_ID, R.Time, R.Content, count(T.RT_ID) AS Thumbs,
    #     #         if(U.Response_ID is null, false, true) AS is_Thumbed, if(L.Post_ID is null, false, true) AS correct_Label
    #     #     FROM ms3.Response R
    #     #         LEFT JOIN ms3.Response_Thumbs T ON R.Response_ID = T.Response_ID
    #     #         LEFT JOIN (
    #     #             SELECT Response_ID, User_ID
    #     #             FROM ms3.Response_Thumbs
    #     #             WHERE User_ID = %s
    #     #         ) U ON R.Response_ID = U.Response_ID
    #     #         LEFT JOIN (
    #     #             SELECT Post_ID, Label
    #     #             FROM ms3.Post
    #     #             WHERE Label = %s
    #     #         ) L ON R.Post_ID = L.Post_ID
    #     #     GROUP BY R.Response_ID
    #     #     HAVING correct_Label = TRUE;
    #     # """
    #     sql2 = """
    #         SELECT *
    #         FROM (
    #             SELECT R.Response_ID, R.Post_ID, R.User_ID, count(T.RT_ID) AS Thumbs, if(U.Response_ID is null, false, true) AS is_Thumbed
    #             FROM ms3.Response R
    #                 LEFT JOIN ms3.Response_Thumbs T ON R.Response_ID = T.Response_ID
    #                 LEFT JOIN (
    #                     SELECT Response_ID, User_ID
    #                     FROM ms3.Response_Thumbs
    #                     WHERE User_ID = %s
    #                 ) U ON R.Response_ID = U.Response_ID
    #                 RIGHT JOIN (
    #                     SELECT Post_ID, Label
    #                     FROM ms3.Post
    #                     WHERE Label = %s
    #                     LIMIT 5
    #                 ) L ON R.Post_ID = L.Post_ID
    #             GROUP BY R.Response_ID
    #         ) A
    #         WHERE Response_ID IS NOT NULL;
    #     """
    #     cur = conn.cursor()
    #     try:
    #         cur.execute(sql2, args=(user_id, label))
    #         res = cur.fetchall()
    #         if res:
    #             response = {'success': True, 'data': res}
    #         else:
    #             response = {'success': False, 'message': 'Not Found', 'data': res}
    #     except pymysql.Error as e:
    #         print(e)
    #         response = {'success': False, 'message': str(e)}
    #     return {"post": post, "response": response}

    def get_post_by_id(user_id, post_id):

        conn = ForumPostResource._get_connection()

        ## return post details
        sql1 = """
            SELECT P.Post_ID, P.Title, P.User_ID, P.Time, P.Location_ID, L.Name AS Location, L.Map_URL, P.Label, P.Content, P.Edited,
                count(T.PT_ID) AS Thumbs, if(U.Post_ID is null, false, true) AS is_Thumbed
            FROM ms3.Post P
                LEFT JOIN ms3.Location L ON P.Location_ID = L.Location_ID
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
                post = {'success': True, 'post_data': res}
                for apost in res:
                    print(apost)
                    userid_post = apost['User_ID']
                    user_info = requests.get(f'{os.environ.get("MS2_URL")}api/userprofile3/{userid_post}').json()['data'][0]
                    apost['profile_pic'] = user_info['profile_pic']
                    apost['username'] = user_info['username']
            else:
                post = {'success': False, 'message': 'Not Found', 'post_data': res}

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
            cur.execute(sql2, args=(user_id, post_id))
            # if success
            res = cur.fetchall()
            if res:
                response = {'success': True, 'resp_data': res}
                for aresponse in res:
                    print(apost)
                    userid_response = aresponse['User_ID']
                    user_info = requests.get(f'{os.environ.get("MS2_URL")}api/userprofile3/{userid_response}').json()['data'][0]
                    aresponse['profile_pic'] = user_info['profile_pic']
                    aresponse['username'] = user_info['username']
            else:
                response = {'success': False, 'message': 'Not Found', 'resp_data': res}
            
        except pymysql.Error as e:
            print(e)
            response = {'success': False, 'message': str(e)}
            return response

        return {"post": post, "response": response}

    def get_resp_by_id(user_id, resp_id):

        conn = ForumPostResource._get_connection()

        sql = """
            SELECT R.*
            FROM ms3.Response R
            WHERE R.Response_ID = %s;
        """
        cur = conn.cursor()
        try:
            cur.execute(sql, resp_id)
            res = cur.fetchall()
            if res:
                response = {'success': True, 'resp_data': res}
            else:
                response = {'success': False, 'message': 'Not Found', 'resp_data': res}
        except pymysql.Error as e:
            print(e)
            response = {'success': False, 'message': str(e)}
            return response

        return response

    # def get_my_posts(user_id):
    #
    #     conn = ForumPostResource._get_connection()
    #
    #     ## return post details
    #     sql1 = """
    #         SELECT P.Post_ID, P.Title, P.User_ID, P.Time, L.Name AS Location, L.Map_URL, P.Label, count(T.PT_ID) AS Thumbs,
    #             if(U.Post_ID is null, false, true) AS is_Thumbed, P.Edited As is_Edited
    #         FROM ms3.Post P
    #             LEFT JOIN ms3.Location L ON P.Location_ID = L.Location_ID
    #             LEFT JOIN ms3.Post_Thumbs T ON P.Post_id = T.Post_id
    #             LEFT JOIN (
    #                 SELECT Post_ID
    #                 FROM ms3.Post_Thumbs
    #                 WHERE User_ID = %s
    #             ) U ON P.Post_ID = U.Post_ID
    #         WHERE P.User_ID = %s
    #         GROUP BY P.Post_id;
    #     """
    #     cur = conn.cursor()
    #     try:
    #         cur.execute(sql1, args=(user_id, user_id))
    #         # if success
    #         res = cur.fetchall()
    #         if res:
    #             post = {'success': True, 'data': res}
    #         else:
    #             post = {'success': False, 'message': 'Not Found', 'data': res}
    #     except pymysql.Error as e:
    #         print(e)
    #         post = {'success': False, 'message': str(e)}
    #
    #     ## return responses
    #     # sql2 = """
    #     #     SELECT R.Response_ID, R.Post_ID, R.User_ID, R.Time, R.Content, count(T.RT_ID) AS Thumbs,
    #     #         if(U.Response_ID is null, false, true) AS is_Thumbed,  if(L.Post_ID is null, false, true) AS mypost
    #     #     FROM ms3.Response R
    #     #         LEFT JOIN ms3.Response_Thumbs T ON R.Response_ID = T.Response_ID
    #     #         LEFT JOIN (
    #     #             SELECT Response_ID, User_ID
    #     #             FROM ms3.Response_Thumbs
    #     #             WHERE User_ID = %s
    #     #         ) U ON R.Response_ID = U.Response_ID
    #     #         LEFT JOIN (
    #     #             SELECT Post_ID, User_ID
    #     #             FROM ms3.Post
    #     #             WHERE User_ID = %s
    #     #         ) L ON R.Post_ID = L.Post_ID
    #     #     GROUP BY R.Response_ID
    #     #     HAVING mypost = TRUE;
    #     # """
    #     sql2 = """
    #         SELECT *
    #         FROM (
    #             SELECT R.Response_ID, R.Post_ID, R.User_ID, R.Time, R.Content, count(T.RT_ID) AS Thumbs,
    #                 if(U.Response_ID is null, false, true) AS is_Thumbed, R.Edited As is_Edited
    #             FROM ms3.Response R
    #                 LEFT JOIN ms3.Response_Thumbs T ON R.Response_ID = T.Response_ID
    #                 LEFT JOIN (
    #                     SELECT Response_ID, User_ID
    #                     FROM ms3.Response_Thumbs
    #                     WHERE User_ID = %s
    #                 ) U ON R.Response_ID = U.Response_ID
    #                 RIGHT JOIN (
    #                     SELECT Post_ID, User_ID
    #                     FROM ms3.Post
    #                     WHERE User_ID = %s
    #                 ) L ON R.Post_ID = L.Post_ID
    #             GROUP BY R.Response_ID
    #         ) A
    #         WHERE Response_ID IS NOT NULL;
    #     """
    #     cur = conn.cursor()
    #     try:
    #         cur.execute(sql2, args=(user_id, user_id))
    #         # if success
    #         res = cur.fetchall()
    #         if res:
    #             response = {'success': True, 'data': res}
    #         else:
    #             response = {'success': False, 'message': 'Not Found', 'data': res}
    #     except pymysql.Error as e:
    #         print(e)
    #         response = {'success': False, 'message': str(e)}
    #
    #     return {"post": post, "response": response}

    @staticmethod
    def location_lookup(line1, line2, city, state, zipcode):
        auth_id = "2b3776cb-23dd-3197-5bee-358c9aed0cb2"
        auth_token = "rTmcnZG9bg5nN95rTJp3"

        credentials = StaticCredentials(auth_id, auth_token)
        client = ClientBuilder(credentials).with_licenses(["us-core-cloud"]).build_us_street_api_client()

        lookup = StreetLookup()
        lookup.street = line1
        lookup.secondary = line2
        lookup.city = city
        lookup.state = state
        lookup.zipcode = zipcode
        lookup.candidates = 3
        lookup.match = "strict"

        try:
            client.send_lookup(lookup)
        except exceptions.SmartyException as err:
            print(err)
            return

        result = lookup.result

        if not result:
            print("No candidates. The address is not valid.")
            res = {"success": False,
                   "message": "No valid address found via Smarty"}
        else:
            first_candidate = result[0]
            print("Valid Street Address: " + first_candidate.delivery_line_1)
            print("Valid City Address: " + first_candidate.last_line)
            full_address = "{}, {}".format(first_candidate.delivery_line_1, first_candidate.last_line)
            res = {"success": True,
                   "address": full_address,
                   "message": "Valid address found via Smarty"}
        return res

    @staticmethod
    def add_location(name, address):
        sql_query = "SELECT COUNT(Location_ID) FROM ms3.Location;"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        url_address = address.replace(" ", "+")
        url_address = url_address.replace(",", "%2C")
        gmap_url = "https://www.google.com/maps/place/{}".format(url_address)
        try:
            cur.execute(sql_query)
            key, val1 = next(iter(cur.fetchone().items()))
            cur.execute("INSERT INTO ms3.Location (Name, Address, Map_URL) VALUES (%s, %s, %s);", args=(name, address, gmap_url))
            cur.execute(sql_query)
            key, val2 = next(iter(cur.fetchone().items()))
            if val2 - val1 == 1:
                result = {'success': True, 'message': 'address added'}
            else:
                result = {'success': False, 'message': 'address not added'}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def add_post_with_new_location(user_id, post_id, title, location, label, content, name, street, city, state):
        print(location)
        if location == '':
            print("in first if")
            input_location = ForumPostResource.location_lookup(street, " ", city, state, " ")
            if input_location["success"]:
                print("in second if")
                input_location_address = input_location["address"]
                print(input_location_address)
                new_location = ForumPostResource.add_location(name, input_location_address)
                if new_location["success"]:
                    print("in third if")
                    sql = "SELECT MAX(Location_ID) FROM ms3.Location;"
                    conn = ForumPostResource._get_connection()
                    cur = conn.cursor()
                    try:
                        cur.execute(sql)
                        key, val = next(iter(cur.fetchone().items()))
                        print(val)
                        resp = {"location": "new", "result": ForumPostResource.add_post(user_id, post_id, title, val, label, content)}
                    except pymysql.Error as e:
                        print(e)
                        return {'success': False, 'message': str(e)}
                else:
                    resp = {"location": "valid but not registered (or already registered). sticking with none", "result": ForumPostResource.add_post(user_id, post_id, title, None, label, content)}
            else:
                resp = {"location": "invalid. sticking with none", "result": ForumPostResource.add_post(user_id, post_id, title, None, label, content)}
        else:
            resp = {"location": "as provided", "result": ForumPostResource.add_post(user_id, post_id, title, location, label, content)}
        return resp

    @staticmethod
    def add_post(user_id, post_id, title, location, label, content):
        t = str(datetime.now())
        sql_query = "SELECT COUNT(Post_ID) FROM ms3.Post;"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql_query)
            key, val1 = next(iter(cur.fetchone().items()))
            if post_id == 0:
                if location == 'None' and label == 'None':
                    cur.execute("INSERT INTO ms3.Post (Title, User_ID, Time, Content) VALUES (%s, %s, %s, %s);", args=(title, user_id, t, content))
                elif location == 'None' and label != 'None':
                    cur.execute("INSERT INTO ms3.Post (Title, User_ID, Time, Label, Content) VALUES (%s, %s, %s, %s, %s);", args=(title, user_id, t, label, content))
                elif location != 'None' and label == 'None':
                    cur.execute("INSERT INTO ms3.Post (Title, User_ID, Time, Location_ID, Content) VALUES (%s, %s, %s, %s, %s);", args=(title, user_id, t, location, content))
                else:
                    cur.execute("INSERT INTO ms3.Post (Title, User_ID, Time, Location_ID, Label, Content) VALUES (%s, %s, %s, %s, %s, %s);", args=(title, user_id, t, location, label, content))
            else:
                if location == 'None' and label == 'None':
                    cur.execute("INSERT INTO ms3.Post (Post_ID, Title, User_ID, Time, Content, Edited) VALUES (%s, %s, %s, %s, %s, %s);", args=(post_id, title, user_id, t, content, 1))
                elif location == 'None' and label != 'None':
                    cur.execute("INSERT INTO ms3.Post (Post_ID, Title, User_ID, Time, Label, Content, Edited) VALUES (%s, %s, %s, %s, %s, %s, %s);", args=(post_id, title, user_id, t, label, content, 1))
                elif location != 'None' and label == 'None':
                    cur.execute("INSERT INTO ms3.Post (Post_ID, Title, User_ID, Time, Location_ID, Content, Edited) VALUES (%s, %s, %s, %s, %s, %s, %s);", args=(post_id, title, user_id, t, location, content, 1))
                else:
                    cur.execute("INSERT INTO ms3.Post (Post_ID, Title, User_ID, Time, Location_ID, Label, Content, Edited) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", args=(post_id, title, user_id, t, location, label, content, 1))
            cur.execute(sql_query)
            key, val2 = next(iter(cur.fetchone().items()))
            if val2 - val1 == 1:
                if post_id == 0:
                    result = {'success': True, 'message': 'post added'}
                else:
                    result = {'success': True, 'message': 'post edited'}
            else:
                if post_id == 0:
                    result = {'success': False, 'message': 'post not added'}
                else:
                    result = {'success': False, 'message': 'post not edited'}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def add_response(user_id, resp_id, post_id, content):
        t = str(datetime.now())
        sql_query_post = "SELECT Title FROM ms3.Post WHERE Post_ID = %s;"
        sql_query_resp = "SELECT COUNT(Response_ID) FROM ms3.Response WHERE Post_ID = %s;"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql_query_post, post_id)
            res = cur.fetchall()
            if res:
                post_result = {'success': True, 'message': 'post found'}
                print("first success")
            else:
                post_result = {'success': False, 'message': 'post not found, cannot add response'}
                print("first fail")
        except pymysql.Error as e:
            print(e)
            post_result = {'success': False, 'message': str(e)}

        try:
            cur.execute(sql_query_resp, post_id)
            key, val1 = next(iter(cur.fetchone().items()))
            if resp_id == 0:
                cur.execute("INSERT INTO ms3.Response (Post_ID, User_ID, Time, Content) VALUES (%s, %s, %s, %s);", args=(post_id, user_id, t, content))
            else:
                cur.execute("INSERT INTO ms3.Response (Response_ID, Post_ID, User_ID, Time, Content, Edited) VALUES (%s, %s, %s, %s, %s, %s);", args=(resp_id, post_id, user_id, t, content, 1))
            cur.execute(sql_query_resp, post_id)
            key, val2 = next(iter(cur.fetchone().items()))
            if val2 - val1 == 1:
                if resp_id == 0:
                    resp_result = {'success': True, 'message': 'response added to post'}
                    print("success adding response")
                else:
                    resp_result = {'success': True, 'message': 'response edited'}
                    print("success editing response")
            else:
                if resp_id == 0:
                    resp_result = {'success': False, 'message': 'post found but response not added'}
                    print("response not added")
                else:
                    resp_result = {'success': False, 'message': 'response not edited'}
                    print("response not edited")
        except pymysql.Error as e:
            print(e)
            resp_result = {'success': False, 'message': str(e)}

        return {'post': post_result, 'response': resp_result}

    def update_post(user_id, post_id, title, location, label, content, ori_user_id, ori_title, ori_location, ori_label, ori_content):
        if user_id == str(ori_user_id):
            print("Post exists and about to be edited")
        else:
            print("Post exists but it cannot be edited by this user")
            return {'success': False, 'message': "Post exists but the current user cannot edit it."}

        if label == "None":
            label = 'Others'
        elif str.isdigit(label):
            label_cat = ('-', 'Administrative', 'Lost and Found', 'Call for Partners', 'Others')
            label = label_cat[int(label)]
        if (title == ori_title) & (location == str(ori_location)) & (label == ori_label) & (content == ori_content):
            print("Post exists, edit received, but this update does not edit the post.")
            rsp = {'success': True, 'message': "New input is similar to the original and post is unedited in this attempt."}
        else:
            t = str(datetime.now())
            conn = ForumPostResource._get_connection()
            cur = conn.cursor()
            try:
                if location == 'None':
                    sql = """
                        UPDATE ms3.Post
                        SET Title = %s, Location_ID = NULL, Label = %s, Content = %s, Time = %s, Edited = 1
                        WHERE Post_ID = %s AND User_ID = %s;
                    """
                    cur.execute(sql, args=(title, label, content, t, post_id, user_id))
                else:
                    sql = """
                        UPDATE ms3.Post
                        SET Title = %s, Location_ID = %s, Label = %s, Content = %s, Time = %s, Edited = 1
                        WHERE Post_ID = %s AND User_ID = %s;
                    """
                    cur.execute(sql, args=(title, location, label, content, t, post_id, user_id))
                print("Post exists, edit received, and this update edited the post.")
                rsp = {"success": True, "message": "Post updated"}
            except pymysql.Error as e:
                print(e)
                rsp = {'success': False, 'message': str(e)}
        return rsp

    def update_response(user_id, resp_id, content, ori_user_id, ori_content):
        if user_id == str(ori_user_id):
            print("Response exists and about to be edited")
        else:
            print("Response exists but it cannot be edited by this user")
            return {'success': False, 'message': "Response exists but the current user cannot edit it."}

        if content == ori_content:
            print("Response exists, edit received, but this update does not edit the response.")
            rsp = {'success': True, 'message': "New input is similar to the original and response is unedited in this attempt."}
        else:
            t = str(datetime.now())
            sql = """
                UPDATE ms3.Response
                SET Content = %s, Time = %s, Edited = 1
                WHERE Response_ID = %s AND User_ID = %s
            """
            conn = ForumPostResource._get_connection()
            cur = conn.cursor()
            try:
                cur.execute(sql, args=(content, t, resp_id, user_id))
                rsp = {"success": True, "message": "Response updated"}
            except pymysql.Error as e:
                print(e)
                rsp = {'success': False, 'message': str(e)}
        return rsp

    def post_delete(post_id):
        sql_query = "SELECT Post_ID FROM ms3.Post WHERE Post_ID = %s"
        sql_delete = "DELETE FROM ms3.Post WHERE post_id = %s"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql_query, post_id)
            res = cur.fetchall()
            if res:
                cur.execute(sql_delete, post_id)
                result = {'success': True, 'message': 'Post deleted successfully'}
            else:
                result = {'success': False, 'message': 'Post not found'}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def resp_delete(resp_id):
        sql_query = "SELECT Response_ID FROM ms3.Response WHERE Response_ID = %s"
        sql_delete = "DELETE FROM ms3.Response WHERE Response_ID = %s"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql_query, resp_id)
            res = cur.fetchall()
            if res:
                cur.execute(sql_delete, resp_id)
                result = {'success': True, 'message': 'Response deleted successfully'}
            else:
                result = {'success': False, 'message': 'Response not found'}
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

    def get_labels():
        sql = "SELECT DISTINCT(Label) FROM ms3.Post ORDER BY Label;"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            res = cur.fetchall()
            label = list(set([x['Label'] for x in res]))
            label = [i for i in label if i is not None]
            result = {'success': True, 'labels': label}
        except pymysql.Error as e:
            print(e)
            result = {'success': False, 'message': str(e)}
        return result

    def get_locations():
        sql = "SELECT Location_ID, Name, Address FROM ms3.Location;"
        conn = ForumPostResource._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            res = cur.fetchall()
            result = {'success': True, 'locations': res}
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

