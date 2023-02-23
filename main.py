from TransferVillage import create_app
from TransferVillage.main.views import *
from TransferVillage.models import *

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
