"""
A sample Hello World server.
"""
import os
import time
import threading
from flask import Flask, render_template
from x_analyzer_proxy import main as x_analyzer_main
from x_token_deploy import main as x_token_deploy_main

# pylint: disable=C0103
app = Flask(__name__)

def run_x_analyzer_periodically():
    """Function to run x_analyzer_main every 120 seconds."""
    while True:
        x_analyzer_main()
        x_token_deploy_main()
        time.sleep(300)

# Start the background thread at the beginning of your application
analyzer_thread = threading.Thread(target=run_x_analyzer_periodically)
analyzer_thread.start()

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
