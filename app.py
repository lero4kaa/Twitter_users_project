from flask import Flask, render_template, request, redirect, url_for
import task3


app = Flask(__name__)
app.config["DEBUG"] = True
@app.route('/', methods=["GET", "POST"])
def index_page():
    if request.method == "GET":
        return render_template("start_page.html")

    smth = task3.main(request.form['contents'])

    if smth is None:
        return render_template("wrong_acc.html")
    return redirect(url_for('maps'))


@app.route('/map')
def maps():
    return render_template("map_with_friends.html")
