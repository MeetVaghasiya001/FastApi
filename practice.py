from fastapi import FastAPI, HTTPException
from pydantic import BaseModel 
from typing import Optional
from db import *
import random


app = FastAPI()

class User(BaseModel):
    user_name: Optional[str]
    password: Optional[str]
    email : Optional[str] 
    age : Optional[int] 


@app.post('/user/add')
def add_user(user: User):
    conn,cur = connection()
    cur.execute("SELECT 1 FROM users WHERE username=%s or email = %s", (user.user_name,user.email))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if user.age <=10 :
        return {
            'message': f'{user.age} is not valid it must be above 10!'
        }
    
    cur.execute("SELECT u_id FROM users")
    ids = [i[0] for i in cur.fetchall()]
    unique_id = random.randint(1000,9999)
    if unique_id in ids:
        raise HTTPException(status_code=400, detail="User Already exists")

    
    cur.execute("INSERT INTO users(u_id,username,password,email,age) VALUES(%s,%s,%s,%s,%s)",(unique_id,user.user_name.strip(),user.password.strip(),user.email.strip(),user.age))
    conn.commit()
    conn.close()
    return {
        "user_name": f'{unique_id} was Genrated !!',
    }


@app.post("/user/login/{user_name}/{password}")
def login(user_name : str , password : str):
    conn,cur = connection()
    cur.execute("SELECT * FROM users WHERE username = %s AND password = %s",(user_name,password))

    user = cur.fetchone()
    if user:
        conn.close()
        return {
            'message':'Login success',
            'details':{
                'user_name':user[1],
                'email':user[3],
                'age':user[-1],
            },
            }
    else:
        conn.close()
        raise HTTPException(status_code=404,detail="User Not Found")


@app.get("/")
def all_users():
    conn,cur = connection()
    cur.execute("SELECT * FROM users")
    users = [{
        'user_id':i[0],
        'user_name':i[1],
        'email':i[3],
        'age':i[4]
    } for i in cur.fetchall()]
    if users:
        return {
            'all_users':users,
            'total_users':len(users)
        }
    else:
        raise HTTPException(status_code=404,detail="You Dont Have Any User!!")

@app.get("/user/info/{id}")
def user_detailes(id:int):
    conn,cur = connection()
    cur.execute("SELECT * FROM users WHERE u_id = %s",(id,))
    user = cur.fetchone()
    if user:
        return {
            'message':'User Found!',
            'details':{
                'user_name':user[1],
                'email':user[3],
                'age':user[-1],
            }
        }
    conn.close()
    
    raise HTTPException(status_code=404,detail="User not found")


@app.patch("/user/update/{id}")
def update_user(id: int, user: User):
    conn, cur = connection()

    cur.execute("SELECT 1 FROM users WHERE u_id=%s", (id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    fields = []
    values = []

    if user.user_name and user.user_name != "string":
        fields.append("username=%s")
        values.append(user.user_name)

    if user.password and user.password != "string":
        fields.append("password=%s")
        values.append(user.password)

    if user.email and user.email != "string":
        fields.append("email=%s")
        values.append(user.email)

    if user.age and user.age != 0:
        if user.age <= 10 :
            return {
                'message':'Age is above 10'
            }
        else:
            fields.append("age=%s")
            values.append(user.age)

    if not fields:
        conn.close()
        raise HTTPException(status_code=400, detail="No data provided")

    values.append(id)

    cur.execute("SELECT * FROM users WHERE username = %s or email =%s",(user.user_name.strip(),user.email.strip()))
    if cur.fetchone():
        return {
            'message':'Data Already in Exists'
        }
    else:
        query = f"UPDATE users SET {', '.join(fields)} WHERE u_id=%s"
        cur.execute(query, tuple(values))

        conn.commit()
        conn.close()

        return {"message": "User updated successfully"}


@app.delete("/user/delete/{user_id}")
def delete_user(user_id: int):
    conn,cur = connection()
    cur.execute("SELECT u_id FROM users")
    ids = [i[0] for i in cur.fetchall()]

    if user_id in ids:
        cur.execute("DELETE FROM users WHERE u_id = %s",(user_id,))
        conn.commit()
        conn.close()
        return {
            'message':f'User {user_id} delete successfully'
        }

    raise HTTPException(status_code=404, detail="User not found")





