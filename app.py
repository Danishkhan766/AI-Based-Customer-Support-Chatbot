from flask import Flask, render_template, request, jsonify
import mysql.connector
import difflib
import random

app = Flask(__name__)

chat_history = []

# ================= MYSQL CONNECTION =================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin@123",
        database="chatbot_db"
    )

# ================= CHATBOT NLP LOGIC =================
def get_response(user_input):
    if not user_input or user_input.strip() == "":
        return "Please type something"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT question, answer FROM data")
        rows = cursor.fetchall()

        best_matches = []
        highest_ratio = 0

        for question, answer in rows:
            ratio = difflib.SequenceMatcher(
                None, user_input.lower(), question.lower()
            ).ratio()

            # collect multiple good matches
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_matches = [answer]
            elif ratio == highest_ratio:
                best_matches.append(answer)

        conn.close()

        # random response from best matches
        if highest_ratio > 0.5 and best_matches:
            return random.choice(best_matches)
        else:
            return "Sorry, I didn't understand."

    except Exception as e:
        print("Chatbot Error:", e)
        return "Server error"

# ================= ROUTES =================

# homepage route
@app.route("/")
def home():
    return render_template("index.html")

# admin route
@app.route("/admin")
def admin():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM data")
        rows = cursor.fetchall()

        conn.close()

        return render_template("admin.html", data=rows)

    except Exception as e:
        print("Admin Error:", e)   # 👈 terminal me show hoga
        return str(e)              # 👈 browser me exact error show hoga

# add data (admin)
@app.route("/add", methods=["POST"])
def add():
    try:
        question = request.form.get("question")
        answer = request.form.get("answer")

        if not question or not answer:
            return "Question and Answer required"

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO data (question, answer) VALUES (%s, %s)",
            (question, answer)
        )

        conn.commit()
        conn.close()

        return admin()

    except Exception as e:
        print("Add Error:", e)
        return "Insert error"
    

    

# delete data (admin)
@app.route("/delete", methods=["POST"])
def delete():
    try:
        id = request.form.get("id")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM data WHERE id=%s", (id,))

        conn.commit()
        conn.close()

    except Exception as e:
        print("Delete Error:", e)

    return admin()

# chatbot route
@app.route("/get", methods=["POST"])
def chatbot():
    try:
        user_msg = request.form.get("msg")
        response = get_response(user_msg)

        # save history
        chat_history.append({
            "user": user_msg,
            "bot": response
        })

        return jsonify({"reply": response})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "Server error"})

# chat history route
@app.route("/history")
def history():
    return jsonify(chat_history)

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)