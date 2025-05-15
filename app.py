from flask import Flask, render_template, request, redirect, session, url_for
from transformers import pipeline
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a secure key in production

# MySQL DB connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="chatbot_db"
)
cursor = db.cursor()

# Sentiment Analysis Pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

def get_response(sentiment):
    if sentiment == 'POSITIVE':
        return "That's great! How can I assist you further?"
    elif sentiment == 'NEGATIVE':
        return "I'm sorry to hear that. Let me help you with that."
    else:
        return "Thanks for your feedback. Let me know how I can help you."

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_input = request.form['user_input']
        sentiment_result = sentiment_pipeline(user_input)[0]
        sentiment = sentiment_result['label']
        bot_reply = get_response(sentiment)
        cursor.execute("INSERT INTO chat_history (username, user_input, bot_reply, sentiment) VALUES (%s, %s, %s, %s)",
                       (session['username'], user_input, bot_reply, sentiment))
        db.commit()
        return render_template('chat.html', user_input=user_input, bot_reply=bot_reply, sentiment=sentiment)
    return render_template('chat.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
