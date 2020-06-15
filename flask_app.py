#!/usr/bin/python3.6
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, render_template
from legislatorsearch import trigger_search

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=["GET", "POST"])

def adder_page():
    errors = ""
    if request.method == "POST":
        zipcode = None
        try:
            zipcode = request.form.get("zipcode")
        except:
            return render_template('new_error.html').format(error_message="We need at least your zipcode to retrieve your local officials!")

        try:
            user_name = request.form["user_name"]
        except:
            errors += "<p> please input an actual name! this is going to your representatives".format(request.form["user_name"])

        if zipcode is not None:
            zipcode=zipcode.strip()
            if user_name.strip() =="":
                user_name = "[YOUR NAME HERE]"
            returned_tags = trigger_search(zipcode,user_name)
            if "error" in returned_tags:
                error_message = returned_tags.split("error:")[1].strip()
                return render_template('new_error.html').format(error_message = error_message)
            result = ''.join(returned_tags)
            return render_template('new_response.html').format(result=result)

    return render_template('new_landing.html').format(errors=errors)