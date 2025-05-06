class Config:
    SECRET_KEY = 'un_secreto_seguro_para_MNDefender'  # En producción, usar variables de entorno
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://alberto:svaia@localhost:3306/svaia'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
