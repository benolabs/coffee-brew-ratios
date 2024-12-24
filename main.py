from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ValidationError, Field
from typing import List, Optional
from uuid import UUID, uuid4
import mysql.connector
from dotenv import load_dotenv
import os

app = FastAPI()
load_dotenv()

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

db = mysql.connector.connect(
  host=MYSQL_HOST,
  user=MYSQL_USER,
  password=MYSQL_PASSWORD,
  database=MYSQL_DATABASE
)

mycursor = db.cursor()

# mycursor.execute("CREATE TABLE coffeebrews (dose VARCHAR(50), yields VARCHAR(50), ratio VARCHAR(50), coffeebeanname VARCHAR(50), grindsize VARCHAR(50), comments VARCHAR(50), coffeeID int PRIMARY KEY AUTO_INCREMENT) AUTO_INCREMENT = 0;")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class UserForm(BaseModel):
    dose: int
    yields: int
    coffeebeanname: str = Field(min_length=1, max_length=500)
    grindsize: int
    comments: str = Field(min_length=1, max_length=500)

def getRatio(dose, yields):
   coffeeground = dose
   coffeeyield = yields
   coffeegroundRatio = round(int(coffeeground) / int(coffeeground))
   coffeeyieldRatio = round(int(coffeeyield) / int(coffeeground))
   ratio = str(coffeegroundRatio) + ':' + str(coffeeyieldRatio)
   return ratio

@app.get('/')
async def name(request: Request):
    try:
        mycursor = db.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM coffeebrews")
        result = mycursor.fetchall()  # Fetch all results
    
    except ValidationError as e:
        return {'error': e.errors()}, 400
    
    finally:
        mycursor.close()

    return templates.TemplateResponse("home.html", {"request": request, "ratios": result})

@app.post("/submit/")
def submit(request: Request, dose: int = Form(...), yields: int = Form(...), comments: str = Form(...), coffeebeanname: str = Form(...), grindsize: int = Form(...)):
    try:
        user = UserForm(dose=dose, yields=yields, comments=comments, coffeebeanname=coffeebeanname, grindsize=grindsize)
        ratio = getRatio(user.dose, user.yields)
        mycursor = db.cursor(dictionary=True)  
        mycursor.execute("INSERT INTO coffeebrews (dose, yields, ratio, coffeebeanname, grindsize, comments) VALUES (%s,%s,%s,%s,%s,%s)", (user.dose, user.yields, ratio, user.coffeebeanname, user.grindsize, user.comments))
        db.commit()
    
    except ValidationError as e:
        return {'error': e.errors()}, 400
    
    finally:
        mycursor.close()

    return RedirectResponse(url=f"/", status_code=303)
        
@app.post("/update/{id}")
async def update(request: Request, id:int, dose: int = Form(...), yields: int = Form(...), comments: str = Form(...), coffeebeanname: str = Form(...), grindsize: int = Form(...)):

    try:
        user = UserForm(dose=dose, yields=yields, comments=comments, coffeebeanname=coffeebeanname, grindsize=grindsize)
        newRatio = getRatio(user.dose, user.yields)
        mycursor = db.cursor(dictionary=True) 
        query = """
        UPDATE coffeebrews
        SET dose = %s, yields = %s, ratio = %s, comments = %s, coffeebeanname = %s, grindsize = %s
        WHERE coffeeID = %s
        """
        mycursor.execute(query, (user.dose, user.yields, newRatio, user.comments, user.coffeebeanname, user.grindsize, id))
        db.commit()
    
    except ValidationError as e:
        return {'error': e.errors()}, 400
    
    finally:
        mycursor.close()

    return RedirectResponse(url=f"/", status_code=303)

@app.get("/delete/{id}")
def delete_recipe(request: Request, id:int):
    try:
        mycursor = db.cursor(dictionary=True)
        query = """
        DELETE FROM coffeebrews WHERE coffeeID = %s;
        """
        mycursor.execute(query, (id,))
        db.commit()

    except ValidationError as e:
        return {'error': e.errors()}, 400
    
    finally:
        mycursor.close()
    
    return RedirectResponse(url=f"/", status_code=303)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)