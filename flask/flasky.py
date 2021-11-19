import os
from app import create_app
from dotenv import load_dotenv


load_dotenv()

app = create_app(os.environ.get('FLASK_CONFIG'))


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
