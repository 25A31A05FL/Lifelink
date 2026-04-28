import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore
from pydantic import BaseModel
from typing import List

app = FastAPI(title="LifeLink Blood Management")
templates = Jinja2Templates(directory="templates")

# Firestore setup
# Ensure the GOOGLE_CLOUD_PROJECT environment variable is set in Cloud Run
db = firestore.Client(database="lifelink-database")

class Donor(BaseModel):
    name: str
    blood_group: str
    phone: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.post("/register")
async def register_donor(name: str = Form(...), blood_group: str = Form(...), phone: str = Form(...)):
    donor_data = {
        "name": name,
        "blood_group": blood_group,
        "phone": phone
    }
    # Add to Firestore
    db.collection("donors").add(donor_data)
    return RedirectResponse(url="/register?success=true", status_code=303)

@app.get("/donors", response_class=HTMLResponse)
async def list_donors(request: Request, blood_group: str = None):
    donors_ref = db.collection("donors")
    
    if blood_group and blood_group != "All":
        docs = donors_ref.where("blood_group", "==", blood_group).stream()
    else:
        docs = donors_ref.stream()
        
    donors_list = [doc.to_dict() for doc in docs]
    return templates.TemplateResponse(
        request=request, 
        name="donors.html", 
        context={"donors": donors_list, "selected_group": blood_group}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
