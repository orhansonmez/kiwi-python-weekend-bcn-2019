from flask import Flask, request, jsonify, render_template
import connections
import dateutil.parser

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/search', methods=['GET'])
def search():
    
    source = request.args.get('source')
    destination = request.args.get('destination')
    departure_date = request.args.get('departure_date').split('T')[0]
    
    return jsonify(results=connections.get_connections(source, destination, departure_date))


if __name__ == '__main__':
   app.run()