from flask import Flask
from views import *

app = Flask(__name__)
app.secret_key = 'hello'

app.add_url_rule("/", view_func=home)
app.add_url_rule("/login", view_func=login, methods=["GET", "POST"])
app.add_url_rule("/logout", view_func=logout)
app.add_url_rule("/register", view_func=register, methods=["GET", "POST"])
app.add_url_rule("/profile", view_func=profile, methods=["GET", "POST"])
app.add_url_rule("/delete_user", view_func=delete_user, methods=["GET", "POST"])
app.add_url_rule("/dashboard", view_func=dashboard)
app.add_url_rule("/record/<string:id>", view_func=record)
app.add_url_rule("/create_record", view_func=create_record, methods=["GET", "POST"])
app.add_url_rule("/edit_record/<string:id>", view_func=edit_record, methods=["GET", "POST"])
app.add_url_rule("/delete_record/<string:id>", view_func=delete_record)
app.add_url_rule("/add_consumption/<string:id>", view_func=add_consumption, methods=["GET", "POST"])
app.add_url_rule("/edit_consumption/<string:id>", view_func=edit_consumption, methods=["GET", "POST"])
app.add_url_rule("/edit_record_info/<string:id>", view_func=edit_record_info, methods=["GET", "POST"])

if __name__ == '__main__':
    #sdfsdfsd
    app.run(debug=True)
    