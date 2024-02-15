import bcrypt


def hash_pw(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()


def check_pw(password, hashedpw):
    return bcrypt.checkpw(password.encode('utf-8'), hashedpw.encode('utf-8'))
