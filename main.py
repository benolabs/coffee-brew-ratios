from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ValidationError, Field
from typing import List, Optional
from uuid import UUID, uuid4

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class UserForm(BaseModel):
    dose: str = Field(min_length=1, max_length=3)
    yields: str = Field(min_length=1, max_length=3)
    coffeebeanname: str = Field(min_length=1, max_length=500)
    grindsize: str = Field(min_length=1, max_length=3)
    comments: str = Field(min_length=1, max_length=500)


tasks = []
ratios = []

def getRatio(dose, yields):
   coffeeground = dose
   coffeeyield = yields
   coffeegroundRatio = round(int(coffeeground) / int(coffeeground))
   coffeeyieldRatio = round(int(coffeeyield) / int(coffeeground))
   ratio = str(coffeegroundRatio) + ':' + str(coffeeyieldRatio)
   return ratio

@app.get('/')
async def name(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "ratios": ratios})

@app.post("/submit/")
def submit(request: Request, dose: str = Form(...), yields: str = Form(...), comments: str = Form(...), coffeebeanname: str = Form(...), grindsize: str = Form(...)):
    try:
        user = UserForm(dose=dose, yields=yields, comments=comments, coffeebeanname=coffeebeanname, grindsize=grindsize)
        ratio = getRatio(user.dose, user.yields)  
        ratios.append({'dose': user.dose, 'yield': user.yields, 'ratio':ratio, 'coffeebeanname':user.coffeebeanname, 'grindsize':user.grindsize, 'comments':user.comments})
        print(ratios)
     
        return RedirectResponse(url=f"/", status_code=303)
    except ValidationError as e:
        return {'error': e.errors()}, 400

@app.post("/update/{id}")
async def update(request: Request, id:int, dose: str = Form(...), yields: str = Form(...), comments: str = Form(...), coffeebeanname: str = Form(...), grindsize: str = Form(...)):
    try:
        user = UserForm(dose=dose, yields=yields, comments=comments, coffeebeanname=coffeebeanname, grindsize=grindsize)
        ratios[id]['dose'] = user.dose
        ratios[id]['yield'] = user.yields
        newRatio = getRatio(user.dose, user.yields)
        ratios[id]['ratio'] = newRatio
        ratios[id]['comments'] = user.comments
        ratios[id]['coffeebeanname'] = user.coffeebeanname
        ratios[id]['grindsize'] = user.grindsize
        return RedirectResponse(url=f"/", status_code=303)
    
    except ValidationError as e:
        return {'error': e.errors()}, 400

@app.get("/delete/{id}")
def delete_todo(request:Request, id:int):
    ratios.pop(id)
    print(ratios)
    return RedirectResponse(url=f"/", status_code=303)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)