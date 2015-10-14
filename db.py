import pickledb

"""
functions for our database-checking
the .load()-funciton will create a .db-file if it dosent already exists
"""

DATABASE_NAME = 'calculated_results.db'

def add_result(key,value):
    """
    Adds a key and value to the database-file. the function returns False if the entry already exists. Otherwise True
    """
    db = pickledb.load(DATABASE_NAME, False)
    if db.get(key) == None:
        db.set(key, value)
        db.dump()
        return True
    else:
        return False

def check_for_result(key):
    """
    Checks whether or not a key exists in our database. If it does, function returns the value, otherwise False. 
    """
    db = pickledb.load(DATABASE_NAME, False)
    k = db.get(key)
    if k == None:
        return False
    else:
        return k



