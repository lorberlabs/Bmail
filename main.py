#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Message
import json
from google.appengine import users
from google.appengine.api import urlfetch


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)

open_weather_api = "2b9448f3b7960c3e992c3d62064c5f19"


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}

            user = users.get_current_user()

            if user:
                params["is_logged"] = True
                params["logout_url"] = users.create_logout_url("/")
                params["email"] = user.email()

            else:
                params["is_logged"] = False
                params["loggin_url"] = user.create_login_url("/")

        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))




class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("main.html")


class InboxHandler(BaseHandler):
    def get(self):
        messages = Message.query(Message.deleted == False).fetch()

        params = {"messages": messages}

        return self.render_template("inbox.html", params=params)

    def post(self):
        user= users.get_current_user()

        if not user:
            self.write("You are not logged in")

        author = self.request.get("name")
        email = user.email()
        message = self.request.get("message")

        if not author:
            author = "Anonymous"

        if "<script>" in message:  # One way to fight JS injection
            return self.write("Can't hack me! Na na na na :)")

        msg_object = Message(author_name=author, email=email, message=message.replace("<script>", ""))  # another way to fight JS injection
        msg_object.put()  # save message into database

        return self.redirect_to("guestbook-site")  # see name in route


class MessageEditHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))

        params = {"message": message}

        params = {"message": message}

        return self.render_template("message_edit.html", params=params)

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))

        text = self.request.get("message")
        message.message = text
        message.put()

        return self.redirect_to("inbox-site")


class MessageDeleteHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))

        params = {"message": message}

        return self.render_template("message_delete.html", params=params)

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))

        message.deleted = True  # fake delete
        message.put()

        return self.redirect_to("inbox-site")

class WeatherHandler(BaseHandler):
    def get(self):
        api_url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(location, open_weather_api)
        weather = urlfetch.fetch(api_url)
        json_data= json.loads(weather.content)

        params = {"weather": json_data}

        return self.redner_template("weather.html", params=para

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/inbox', GuestbookHandler, name="inbox-site"),
    webapp2.Route('/message/<message_id:\d+>/edit', MessageEditHandler, name="message-edit"),
    webapp2.Route('/message/<message_id:\d+>/delete', MessageDeleteHandler, name="message-delete"),
     webapp2.Route('/weather', WeatherHandler)
], debug=True)
