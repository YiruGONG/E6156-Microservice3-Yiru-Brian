import logging.handlers

from flask import Flask, Response, request
from flask_cors import CORS
from forum_post_resource import ForumPostResource
from utils import DTEncoder

import json
from datetime import datetime
import socket

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler 
LOG_FILE = '/tmp/sample-app.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)

welcome = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <!--
    Copyright 2012 Amazon.com, Inc. or its affiliates. All Rights Reserved.

    Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

        http://aws.Amazon/apache2.0/

    or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
  -->
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>Welcome</title>
  <style>
  body {
    color: #ffffff;
    background-color: #E0E0E0;
    font-family: Arial, sans-serif;
    font-size:14px;
    -moz-transition-property: text-shadow;
    -moz-transition-duration: 4s;
    -webkit-transition-property: text-shadow;
    -webkit-transition-duration: 4s;
    text-shadow: none;
  }
  body.blurry {
    -moz-transition-property: text-shadow;
    -moz-transition-duration: 4s;
    -webkit-transition-property: text-shadow;
    -webkit-transition-duration: 4s;
    text-shadow: #fff 0px 0px 25px;
  }
  a {
    color: #0188cc;
  }
  .textColumn, .linksColumn {
    padding: 2em;
  }
  .textColumn {
    position: absolute;
    top: 0px;
    right: 50%;
    bottom: 0px;
    left: 0px;

    text-align: right;
    padding-top: 11em;
    background-color: #1BA86D;
    background-image: -moz-radial-gradient(left top, circle, #6AF9BD 0%, #00B386 60%);
    background-image: -webkit-gradient(radial, 0 0, 1, 0 0, 500, from(#6AF9BD), to(#00B386));
  }
  .textColumn p {
    width: 75%;
    float:right;
  }
  .linksColumn {
    position: absolute;
    top:0px;
    right: 0px;
    bottom: 0px;
    left: 50%;

    background-color: #E0E0E0;
  }

  h1 {
    font-size: 500%;
    font-weight: normal;
    margin-bottom: 0em;
  }
  h2 {
    font-size: 200%;
    font-weight: normal;
    margin-bottom: 0em;
  }
  ul {
    padding-left: 1em;
    margin: 0px;
  }
  li {
    margin: 1em 0em;
  }
  </style>
</head>
<body id="sample">
  <div class="textColumn">
    <h1>Congratulations</h1>
    <p>Your first AWS Elastic Beanstalk Python Application is now running on your own dedicated environment in the AWS Cloud</p>
    <p>This environment is launched with Elastic Beanstalk Python Platform</p>
    <p>Test for Yiru, Brain use</p>
  </div>
  
  <div class="linksColumn"> 
    <h2>What's Next?</h2>
    <ul>
    <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/">AWS Elastic Beanstalk overview</a></li>
    <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/index.html?concepts.html">AWS Elastic Beanstalk concepts</a></li>
    <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/create_deploy_Python_django.html">Deploy a Django Application to AWS Elastic Beanstalk</a></li>
    <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/create_deploy_Python_flask.html">Deploy a Flask Application to AWS Elastic Beanstalk</a></li>
    <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/create_deploy_Python_custom_container.html">Customizing and Configuring a Python Container</a></li>
    <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/using-features.loggingS3.title.html">Working with Logs</a></li>

    </ul>
  </div>
</body>
</html>
"""

application = Flask(__name__)
CORS(application)

@application.route('/')
def hello_message():
    return welcome

@application.route('/api/forum/user/<user_id>', methods=["GET"])
def forum(user_id):
    result = ForumPostResource.get_all_posts(user_id)

    if result['success']:
        rsp = Response(json.dumps(result,cls=DTEncoder), status=200, content_type="application.json")
    else:
        rsp = Response("Method failed", status=404, content_type="text/plain")

    return rsp

@application.route('/api/forum/<cat>/user/<user_id>', methods=["GET"])
def forum_cat(user_id, cat):
    # print("cat:", cat, "user_id: ", user_id)
    result = ForumPostResource.get_posts_by_label(user_id, cat)

    if result['response']['success'] and result['response']['success']:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
        print("Found posts with responses")
    elif result['response']['success']:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
        print("Found posts with no responses")
    else:
        rsp = Response("Method failed", status=404, content_type="text/plain")
        print("No posts found")

    return rsp

@application.route('/api/forum/post/<post_id>/user/<user_id>', methods=["GET"])
def forum_post(user_id, post_id):

    result = ForumPostResource.get_post_by_id(user_id, post_id)
    print(result)

    if result['response']['success'] and result['response']['success']:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
        print("Found the post with responses")
    elif result['response']['success']:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
        print("Found the post with no responses")
    else:
        rsp = Response("Method Failed", status=404, content_type="text/plain")
        print("The post not found")

    return rsp

@application.route('/api/forum/myposts/user/<user_id>', methods=["GET"])
def forum_myposts(user_id):

    result = ForumPostResource.get_my_posts(user_id)

    if result['post']['success'] and result['response']['success']:
        rsp = Response(json.dumps(result,cls=DTEncoder), status=200, content_type="application.json")
        print("Found posts with responses")
    if result['post']['success']:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
        print("Found posts with no responses")
    else:
        rsp = Response("Method Failed", status=404, content_type="text/plain")

    return rsp

@application.route('/api/forum/newpost/user/<user_id>', methods=["POST"])
def add_post(user_id):
    if request.method == 'POST':
        post_res = ForumPostResource.add_post(user_id,
                                              str(request.get_json()['title']),
                                              str(request.get_json()['location']),
                                              str(request.get_json()['label']),
                                              str(request.get_json()['content']))
        if post_res['success']:
            res = {'success': True, 'message': 'post successfully added', 'userId': post_res}
            rsp = Response(json.dumps(res), status=200, content_type="application.json")
            print("Post added")
    else:
        rsp = Response("Method failed", status=404, content_type="text/plain")
        print("Post not added")

    return rsp

@application.route('/api/forum/post/<post_id>/edit/user/<user_id>', methods=["GET", "POST"])
def edit_post(user_id, post_id):
    if request.method == 'GET':
        results = ForumPostResource.get_post_by_id(user_id, post_id)["post"]["post_data"][0]
        print("Post exists and could be edited")
        return Response(json.dumps(results, cls=DTEncoder), status=200, content_type="application.json")
    else:

        results = ForumPostResource.update_post(user_id,
                                                post_id,
                                                str(request.get_json()['title']),
                                                str(request.get_json()['location']),
                                                str(request.get_json()['label']),
                                                str(request.get_json()['content']))
        print("Post edited")
        return Response(json.dumps(results, cls=DTEncoder), status=200, content_type="application.json")

@application.route('/api/forum/post/<post_id>/newresponse/user/<user_id>', methods=["POST"])
def add_response(user_id, post_id):
    if request.method == 'POST':
        resp_res = ForumPostResource.add_response(user_id,
                                                  post_id,
                                                  str(request.get_json()['content']))
        if resp_res['response']['success']:
            res = {'success': True, 'message': 'response successfully added', 'details': resp_res}
            rsp = Response(json.dumps(res), status=200, content_type="application.json")
            print("Response added")
    else:
        rsp = Response("Method failed", status=404, content_type="text/plain")
        print("Response not added")
    return rsp

@application.route('/api/forum/post/<post_id>/thumb/user/<user_id>', methods=["POST"])
def thumbs_post(user_id, post_id):
    result = ForumPostResource.click_thumb_post(user_id, post_id)
    if result['success']:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
        print("Post thumbed up")
    else:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
        print("Post thumb status not changed")

    return rsp

@application.route('/api/forum/resp/<resp_id>/thumb/user/<user_id>', methods=["POST"])
def thumbs_response(user_id, resp_id):
    result = ForumPostResource.click_thumb_response(user_id, resp_id)
    if result['success']:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
        print("Response thumb status changed")
    else:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
        print("Response thumb status not changed")

    return rsp

# def sort_post():
#     # TO DO...
#
# def filter_post():
#     # TO DO...
#
# @application.route('/api/forum/mypost/<user_id>/post/<post_id>/edit', methods=["GET","POST"])
# def edit_post(user_id):
#     ###### Not completed yet
#     return None
#
# @application.route('/api/forum/mypost/<user_id>/post/<post_id>/delete', methods=["GET","POST"])
# def delete_post(user_id):
#     ###### Not completed yet
#     return None


if __name__ == '__main__':
    application.run(host="0.0.0.0", port=5012, debug=True)

"""
def application(environ, start_response):
    path = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']
    if method == 'POST':
        try:
            if path == '/':
                request_body_size = int(environ['CONTENT_LENGTH'])
                request_body = environ['wsgi.input'].read(request_body_size)
                logger.info("Received message: %s" % request_body)
            elif path == '/scheduled':
                logger.info("Received task %s scheduled at %s", environ['HTTP_X_AWS_SQSD_TASKNAME'],
                            environ['HTTP_X_AWS_SQSD_SCHEDULED_AT'])
        except (TypeError, ValueError):
            logger.warning('Error retrieving request body for async work.')
        response = ''
    else:
        response = welcome
    start_response("200 OK", [
        ("Content-Type", "text/html"),
        ("Content-Length", str(len(response)))
    ])
    return [bytes(response, 'utf-8')]
"""
