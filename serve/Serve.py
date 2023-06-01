from app.app import create_app

from config import PORT 

class Serve:

    @classmethod
    def standalone(cls, profile):
        app = create_app(profile=profile)
        app.run(host='127.0.0.1', port=PORT)