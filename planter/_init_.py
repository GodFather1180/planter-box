from flask import Flask, jsonify, render_template, request
from flask_apscheduler import APScheduler
from jsonschema import validate

from .control import MotorType, PlanterControl
from .sensor import moisture_level, reservoir_low

schema = {
    "type": "object",
    "properties": {
        "moisture": {"type": "number"},
        "threshold": {"type": "number"},
        "waterStatus": {"type": "string"},
        "waterInterval": {"type": "number"},
        "shadeStatus": {"type": "string"},
    },
}

scheduler = APScheduler()


def create_app(test_config=None, threshold=60, backoff=10, motor=MotorType.DC):
    # Initialize instance
    app = Flask(__name__)
    controller = PlanterControl(threshold, backoff)

    # Routing
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/api/get-moisture", methods=["GET"])
    def read_moisture():
        return jsonify({"moisture": moisture_level()})

    @app.route("/api/set-threshold", methods=["POST"])
    def set_threshold():
        try:
            data = request.get_json()
            validate(data, schema=schema)

            threshold = data.get("threshold")
            controller.moisture_threshold = threshold

            return jsonify({"status": "success", "threshold": threshold}), 200

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    @app.route("/api/<types>", methods=["POST"])
    def handle_request(types):
        try:
            data = request.get_json()
            validate(data, schema=schema)

            if types == "toggle-shade":
                status = data.get("shadeStatus")
                controller.toggle_shade(status)

                return jsonify({"status": "success", "message": "Shade Toggled"}), 200

            elif types == "toggle-water":
                status = data.get("waterStatus")
                period = data.get("waterInterval")
                controller.toggle_water(status, period)

                return jsonify({"status": "success", "message": "Water Toggled"}), 200

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    @scheduler.task("interval", id="update_moisture", seconds=5, misfire_grace_time=900)
    def update_moisture():
        with scheduler.app.app_context():
            controller.update_moisture()

    @scheduler.task("interval", id="auto_shade", seconds=100, misfire_grace_time=900)
    def auto_water():
        with scheduler.app.app_context():
            controller.auto_shade()

    @scheduler.task("interval", id="auto_water", seconds=backoff, misfire_grace_time=900)
    def auto_water():
        with scheduler.app.app_context():
            controller.auto_water()

    scheduler.init_app(app)
    scheduler.start()

    return app