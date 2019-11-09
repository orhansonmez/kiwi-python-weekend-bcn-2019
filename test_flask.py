from flask import Flask
app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/ping')
def ping():
  return 'pong'

if __name__ == '__main__':
   app.run(debug=True)