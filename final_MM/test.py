from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from auth import register_user, login_user
from sentiment_analysis import fetch_and_analyze_for_current_user, get_user_analyzed_data
from pages.graph import get_graph  # Graph function for dynamic graphs
import pandas as pd
import os
import sys

# ✅ UTF-8 encoding for emojis and special characters in console
sys.stdout.reconfigure(encoding='utf-8')

# ✅ Flask app setup
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Random secret key for session security


# ------------------------- ROUTES -------------------------

# ---------- Home / Launch Pages ----------
@app.route('/')
def home():
    return render_template('home.html')  # Landing page


@app.route('/launch')
def launch():
    return render_template('launch.html')  # Navigation to login/signup


# ---------- Registration ----------
@app.route('/sign', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        twitter_username = request.form['twitter_username']

        result = register_user(name, email, password, twitter_username)
        if result == "success":
            flash("🎉 Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash(result, "danger")  # Show error message

    return render_template('sign.html')


# ---------- Login ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = login_user(email, password)
        if isinstance(user, str):  # Error message
            flash(user, "danger")
        else:
            session['user_id'] = user[0]  # Store user ID
            session['twitter_username'] = user[1]  # Store Twitter handle
            flash("✅ Login successful!", "success")
            return redirect(url_for('dashboard'))

    return render_template('login.html')


# ---------- Dashboard with Sentiment Analysis ----------
@app.route('/index')
def dashboard():
    if 'user_id' not in session:
        flash("⚠️ Please log in first.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    twitter_username = session['twitter_username']

    # ✅ Fetch, analyze, and store Twitter data for the user
    analyzed_data = fetch_and_analyze_for_current_user(user_id)

    # ✅ Handle case with no posts
    if not analyzed_data:
        flash("⚠️ No posts found for analysis.", "info")
        return render_template("index.html", data=None, sentiment_data=None, username=twitter_username)

    # ✅ Sentiment analysis breakdown
    df = pd.DataFrame(analyzed_data)
    sentiment_counts = df['svm_prediction'].value_counts().to_dict()

    sentiment_data = {
        "positive": sentiment_counts.get("positive", 0),
        "negative": sentiment_counts.get("negative", 0),
        "neutral": sentiment_counts.get("neutral", 0)
    }

    # ✅ Render dashboard with data
    return render_template(
        "index.html",
        data=analyzed_data,
        sentiment_data=sentiment_data,
        username=twitter_username
    )


# ---------- Dynamic Graphs ----------
app.add_url_rule('/graph', 'get_graph', get_graph)


# ---------- Reports ----------
@app.route('/reports')
def reports():
    if 'user_id' not in session:
        flash("⚠️ Please log in first.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    analyzed_data = get_user_analyzed_data(user_id)

    return render_template("reports.html", data=analyzed_data)


# ---------- Logout ----------
@app.route('/logout')
def logout():
    session.clear()  # Clear session data on logout
    flash("✅ Logged out successfully.", "info")
    return redirect(url_for('login'))


# ---------------------- Run Flask App ----------------------
if __name__ == '__main__':
    app.run(debug=True)
