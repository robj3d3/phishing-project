import time
from phishing import app
from app.models import Staff

with app.app_context():
    while True:
        staff = Staff.query.all()

        for s in staff:
            print(s.staffname)

        time.sleep(3)