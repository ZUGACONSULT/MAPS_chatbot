from flask import Flask, jsonify, render_template, request
from maps import provide_answer

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    # Here you would implement your chatbot logic. For simplicity, we echo the input.
    return jsonify({"message": provide_answer(user_text)})

if __name__ == "__main__":
  app.run(host='0.0.0.0',debug=True)  
  