from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, Flaskbook!"


@app.route("/hello",
        methods=["GET"],
        endpoint ="hello-endpoint")
def hello():
    return "Hello, World"



#템플릿 이용
@app.route("/name/<name>",
            methods=["GET", "POST"],
            endpoint="show_name")
def show_name(name):
    return  render_template("index.html",name=name)

with app.test_request_context():
    #1
    print(url_for("index"))
    # hello/world
    print(url_for("hello-endpoint",name="world"))
    #/name/AK?page=1
    print(url_for("show_name",name="AK", page="1"))
