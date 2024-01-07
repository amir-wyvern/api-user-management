import redis

def set_token(user_id, token, db: redis.Redis):
    return db.set(f'user:token:{user_id}', token, ex=24*60*60*7)

def get_token(user_id, db: redis.Redis):
    return db.get(f'user:token:{user_id}')

def del_token(user_id, db: redis.Redis):
    return db.delete(f'user:token:{user_id}')