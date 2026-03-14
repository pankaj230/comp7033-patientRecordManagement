from app.app import app
import os

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode
    )
