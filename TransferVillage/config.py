import os

class Config:
    # Change this for production server to False
    TESTING = True
    APP_Id = 'f726da3b19'
    APP_SECRET = 'af51d588e020b2785533ef2ce7b901c8224c686f142452065bbb87177143cf15'
    SECRET_KEY = '326994da03a96781108b45daacf39c5b4ca3e23ff6548b7fdacc1292429179f853fe71646b2f5b373ac98a0567a7012e1494'
    if TESTING:
        # Testing database
        SQLALCHEMY_DATABASE_URI = 'sqlite:///TransferVillage.db'
    else:
        # Production database
        DATABASE_PASSWORD = '###**Major**###'
        DATABASE_USER = 'major'
        DATABASE_IP = 'localhost'
        DATABASE_NAME = 'TransferVillage'
        SQLALCHEMY_DATABASE_URI = f'mysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_IP}/{DATABASE_NAME}'

    # Mail Settings
    MAIL_SERVER = 'smtp.zoho.in'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('TransferVillage_Email')
    MAIL_PASSWORD = os.getenv('TransferVillage_Email_Password')

    # AWS Credentials
    AWS_SERVICE_NAME = os.getenv('AWS_SERVICE_NAME')
    AWS_REGION_NAME = os.getenv('AWS_REGION_NAME')
    AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    # File related settings
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'docx', 'jpeg', 'xlsx'}
