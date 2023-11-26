import os
import threading
from app import create_app
from app.utils.load import load_data

app = create_app()

if __name__ == "__main__":
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        # Create a thread that runs the import_data function
        t = threading.Thread(target=load_data)
        t.start()

    app.run(debug=True)
