from flask import Flask, jsonify, render_template, request
from donttrust import Schema

app = Flask(__name__, static_folder='public')

userschema = Schema({
    'threshold': Schema().number().min(0).max(100).required()
})


@app.route("/")
def home():
    return render_template('index.html')


@app.route('/api/get-moisture', methods=['GET'])
#write to read sensor values
@app.route('/api/set-threshold', methods=['POST'])
def set_threshold():
    try:
        data = request.get_json()
        threshold = data.get('threshold')

        result = userschema.validate({'threshold'})

        if result:
            return jsonify({"status": "success", "threshold": threshold}), 200

        else:
            raise ValueError("Invalid threshold value.")

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/<types>', methods=['POST'])
def handle_request(types):
    if types == 'toggle-shade':

        return jsonify({"status": "success", "message": "Shade Toggled"}), 200

    elif types == 'toggle-water':

        return jsonify({"status": "success", "message": "Water Toggled"}), 200


if __name__ == '__main__':
    # Set the port to 5003
    app.run(debug=True, host='0.0.0.0', port=5003)