"""
A sample Hello World server.
"""
import os

from flask import Flask, render_template
# from x_analyzer import main as x_analyzer_main

# pylint: disable=C0103
app = Flask(__name__)

# @app.before_first_request
# def init_app():
#     """Function to run once before the first request after the server starts."""
#     x_analyzer_main()

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    message = "It's running!"

    """Get Cloud Run environment variables."""
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    return render_template('index.html',
        message=message,
        Service=service,
        Revision=revision)

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
