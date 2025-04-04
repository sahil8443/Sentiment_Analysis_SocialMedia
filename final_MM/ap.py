from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Blueprint
import requests 
from auth import register_user, login_user
from sentiment_analysis import analyze_csv, generate_recommendations
from pages.graph import graph_bp
import pandas as pd
import os
import sys
from werkzeug.utils import secure_filename

# Ensure UTF-8 encoding (emoji-safe)
sys.stdout.reconfigure(encoding='utf-8')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Register blueprints
app.register_blueprint(graph_bp, url_prefix='/graph')

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --------------------------- ROUTES --------------------------- #

# ---------- Home / Launch Pages ---------- #
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/launch')
def launch():
    return render_template('launch.html')

# ---------- Registration ---------- #
@app.route('/sign', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        twitter_username = request.form.get('twitter_username', '')  # Get twitter_username with default empty string

        # Call registration logic
        result = register_user(name, email, password, twitter_username)
        if result == "success":
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash(result, "danger")

    return render_template('sign.html')

# ---------- Login ---------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = login_user(email, password)

        if isinstance(user, str):  # Error message
            flash(user, "danger")
        else:
            # Store user ID and name in session
            session['user_id'] = user[0]  # ID
            session['username'] = user[1]  # Name

            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))

    return render_template('login.html')

# ---------- Dashboard ---------- #
@app.route('/index')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    username = session.get('username', 'Unknown User')
    results = session.get('analysis_results', None)
    
    if results:
        # Calculate sentiment counts
        df = pd.DataFrame(results)
        sentiment_counts = df['svm_sentiment'].value_counts().to_dict()
        
        sentiment_data = {
            "positive": sentiment_counts.get("positive", 0),
            "negative": sentiment_counts.get("negative", 0),
            "neutral": sentiment_counts.get("neutral", 0)
        }
        
        recommendations = generate_recommendations(sentiment_data)
    else:
        sentiment_data = None
        recommendations = None
        results = None
    
    return render_template(
        "index.html",
        results=results,
        sentiment_data=sentiment_data,
        recommendations=recommendations,
        username=username
    )

# ---------- Upload ---------- #
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Analyze the CSV file
            results = analyze_csv(filepath)
            if results:
                session['analysis_results'] = results
                flash('File analyzed successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Error analyzing file', 'danger')
                return redirect(request.url)
        else:
            flash('Please upload a CSV file', 'danger')
            return redirect(request.url)
    
    return render_template('upload.html')

# ---------- Report ---------- #
@app.route('/report')
def report():
    # Get analysis results from session
    results = session.get('analysis_results', [])
    if not results:
        return render_template('report.html',
                             sentiment_data={'total': 0},
                             results=[],
                             recommendations=[],
                             model_agreement={'all_agree': 0, 'two_agree': 0, 'none_agree': 0,
                                            'all_agree_percent': 0, 'two_agree_percent': 0, 'none_agree_percent': 0})

    # Convert results to DataFrame for easier analysis
    df = pd.DataFrame(results)
    
    # Calculate sentiment counts
    sentiment_counts = {
        'positive': len(df[df['svm_sentiment'] == 'positive']),
        'neutral': len(df[df['svm_sentiment'] == 'neutral']),
        'negative': len(df[df['svm_sentiment'] == 'negative']),
        'total': len(df)
    }
    
    # Calculate percentages
    total = sentiment_counts['total']
    if total > 0:
        sentiment_counts['positive_percent'] = (sentiment_counts['positive'] / total) * 100
        sentiment_counts['neutral_percent'] = (sentiment_counts['neutral'] / total) * 100
        sentiment_counts['negative_percent'] = (sentiment_counts['negative'] / total) * 100
    else:
        sentiment_counts['positive_percent'] = 0
        sentiment_counts['neutral_percent'] = 0
        sentiment_counts['negative_percent'] = 0

    # Calculate model agreement
    all_agree = len(df[
        (df['svm_sentiment'] == df['lr_sentiment']) &
        (df['lr_sentiment'] == df['bert_sentiment'])
    ])
    
    two_agree = len(df[
        (df['svm_sentiment'] == df['lr_sentiment']) |
        (df['lr_sentiment'] == df['bert_sentiment']) |
        (df['svm_sentiment'] == df['bert_sentiment'])
    ]) - all_agree
    
    none_agree = len(df) - all_agree - two_agree

    # Calculate agreement percentages
    if total > 0:
        model_agreement = {
            'all_agree': all_agree,
            'two_agree': two_agree,
            'none_agree': none_agree,
            'all_agree_percent': (all_agree / total) * 100,
            'two_agree_percent': (two_agree / total) * 100,
            'none_agree_percent': (none_agree / total) * 100
        }
    else:
        model_agreement = {
            'all_agree': 0,
            'two_agree': 0,
            'none_agree': 0,
            'all_agree_percent': 0,
            'two_agree_percent': 0,
            'none_agree_percent': 0
        }

    # Generate recommendations
    recommendations = generate_recommendations(sentiment_counts)

    return render_template('report.html',
                         sentiment_data=sentiment_counts,
                         results=results,
                         recommendations=recommendations,
                         model_agreement=model_agreement)

# ---------- Logout ---------- #
@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# ---------------------- Run Flask App ---------------------- #
if __name__ == '__main__':
    app.run(debug=True)
