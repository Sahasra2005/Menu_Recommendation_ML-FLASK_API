from flask import Flask, jsonify
from menu_generator import get_current_day, increment_day, generate_combo_for_day

app = Flask(__name__)

@app.route('/generate_combo', methods=['GET'])
def generate_combo():
    day = get_current_day()
    result = generate_combo_for_day(day)
    increment_day()
    return jsonify(result)

@app.route('/', methods=['GET'])
def home():
    return generate_combo()

if __name__ == "__main__":
    app.run(debug=True)
