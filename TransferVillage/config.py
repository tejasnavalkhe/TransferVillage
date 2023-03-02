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
        DATABASE_PASSWORD = '#TransferVillageMajor2023'
        DATABASE_USER = 'root'
        DATABASE_IP = 'localhost'
        DATABASE_NAME = 'TransferVillage'
        SQLALCHEMY_DATABASE_URI = f'mysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_IP}/{DATABASE_NAME}'

    # Mail Settings
    MAIL_SERVER = 'smtp.zoho.in'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'support@tejearning.com'
    MAIL_PASSWORD = 'jdV61S6xDJ64'

    # AWS Credentails
    AWS_SERVICE_NAME = 's3'
    AWS_REGION_NAME = 'eu-west-2'
    AWS_BUCKET_NAME = 'transfervillage'
    AWS_ACCESS_KEY_ID = 'AKIAT6T5Y3W3UZ2WI4C2'
    AWS_SECRET_ACCESS_KEY = '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'

    # File related settings
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'docx', 'jpeg', 'xlsx'}
