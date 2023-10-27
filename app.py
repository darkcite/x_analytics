"""
A sample server.
"""
import os
import time
import threading
import logging
from flask import Flask, render_template, jsonify
from x_analyzer_proxy import main as x_analyzer_main
from x_token_deploy import main as x_token_deploy_main

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# pylint: disable=C0103
app = Flask(__name__)

def run_x_analyzer_periodically():
    """Function to run x_analyzer_main every 300 seconds (5 minutes)."""
    while True:
        try:
            logger.info("Tasks started in background thread.")
            x_analyzer_main()
            x_token_deploy_main()
            logger.info("Tasks executed successfully in background thread.")
        except Exception as e:
            logger.error(f"Error executing tasks in background thread: {str(e)}")
        time.sleep(300)

# Start the background thread at the beginning of your application
analyzer_thread = threading.Thread(target=run_x_analyzer_periodically)
analyzer_thread.start()

@app.route('/')
def hello():
    """Return a friendly HTTP greeting and run the tasks."""
    try:
        x_analyzer_main()
        x_token_deploy_main()
        logger.info("Tasks executed successfully via root endpoint.")
        
        message = "Tasks executed and it's running!"
        """Get Cloud Run environment variables."""
        service = os.environ.get('K_SERVICE', 'Unknown service')
        revision = os.environ.get('K_REVISION', 'Unknown revision')

        return render_template('index.html',
            message=message,
            Service=service,
            Revision=revision)
    except Exception as e:
        logger.error(f"Error executing tasks via root endpoint: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
