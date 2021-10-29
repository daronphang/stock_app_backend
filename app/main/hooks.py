from flask import g, session
from app.main import main


@main.after_request
def after_request():
    return
