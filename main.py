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

class Task(BaseModel):
    id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    completed: bool = False

class UserForm(BaseModel):
    dose: str = Field(min_length=1, max_length=3)
    yields: str = Field(min_length=1, max_length=3)
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

@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    task.id = uuid4()
    tasks.append(task)
    return task

@app.post("/submit/")
def submit(request: Request, dose: str = Form(...), yields: str = Form(...), comments: str = Form(...)):
    try:
        user = UserForm(dose=dose, yields=yields, comments=comments)
        ratio = getRatio(user.dose, user.yields)  
        ratios.append({'dose': user.dose, 'yield': user.yields, 'ratio':ratio, 'comments':user.comments})
        print(ratios)
        # return templates.TemplateResponse("home.html", {"request": request, "ratios": ratios})
        return RedirectResponse(url=f"/", status_code=303)
    except ValidationError as e:
        return {'error': e.errors()}, 400

# @app.post("/submit/")
# async def submit(request: Request, dose: str = Form(...), yields: str = Form(...)):
#    ratio = getRatio(dose, yields)
#    ratios.append({'dose': dose, 'yield': yields, 'ratio':ratio})
#    return templates.TemplateResponse("home.html", {"request": request, "ratios": ratios})

@app.post("/update/{id}")
async def update(request: Request, id:int, dose: str = Form(...), yields: str = Form(...), comments: str = Form(...)):
    try:
        user = UserForm(dose=dose, yields=yields, comments=comments)
        ratios[id]['dose'] = user.dose
        ratios[id]['yield'] = user.yields
        newRatio = getRatio(user.dose, user.yields)
        ratios[id]['ratio'] = newRatio
        ratios[id]['comments'] = user.comments
        return RedirectResponse(url=f"/", status_code=303)
    
    except ValidationError as e:
        return {'error': e.errors()}, 400

@app.get("/tasks/", response_model=List[Task])
def read_tasks():
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: UUID):
    for task in tasks:
        if task.id == task_id:
            return task
        
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: UUID, task_update: Task):
    for idx, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = task.copy(update=task_update.dict(exclude_unset=True))
            tasks[idx] = updated_task
            return updated_task
        
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", response_model=Task)
def delete_task(task_id: UUID):
    for idx, task in enumerate(tasks):
        if task.id == task_id:
            return tasks.pop(idx)
    
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/delete/{id}")
def delete_todo(request:Request, id:int):
    ratios.pop(id)
    print(ratios)
    return RedirectResponse(url=f"/", status_code=303)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)