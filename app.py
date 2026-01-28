from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn import run as app_run

from typing import Optional

from us_visa.constants import APP_HOST, APP_PORT
from us_visa.pipeline.prediction_pipeline import USvisaDataset, USvisaClassifier
from us_visa.pipeline.training_pipeline import TrainPipeline

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Data Form Class
# ---------------------------
class DataForm:
    def __init__(self, request: Request):
        self.request = request
        self.education_of_employee = None
        self.has_job_experience = None
        self.requires_job_training = None
        self.no_of_employees = None
        self.company_age = None
        self.prevailing_wage = None
        self.full_time_position = None

    async def get_usvisa_data(self):
        form = await self.request.form()
        self.education_of_employee = form.get("education_of_employee")
        self.has_job_experience = form.get("has_job_experience")
        self.requires_job_training = form.get("requires_job_training")
        self.no_of_employees = form.get("no_of_employees")
        self.company_age = form.get("company_age")
        self.prevailing_wage = form.get("prevailing_wage")
        self.full_time_position = form.get("full_time_position")

# ---------------------------
# Routes
# ---------------------------

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "usvisa.html",
        {"request": request, "context": "Fill the form to predict visa status"},
    )

@app.get("/train")
async def trainRouteClient():
    try:
        TrainPipeline().run_pipeline()
        return Response("Training successful !!")
    except Exception as e:
        return Response(f"Error Occurred! {e}")

@app.post("/")
async def predictRouteClient(request: Request):
    try:
        form = DataForm(request)
        await form.get_usvisa_data()

        usvisa_data = USvisaDataset(
            education_of_employee=form.education_of_employee,
            has_job_experience=form.has_job_experience,
            requires_job_training=form.requires_job_training,
            no_of_employees=form.no_of_employees,
            company_age=form.company_age,
            prevailing_wage=form.prevailing_wage,
            full_time_position=form.full_time_position,
        )

        df = usvisa_data.get_usvisa_input_data_frame()

        predictor = USvisaClassifier()
        prediction = predictor.predict(df)[0]

        if prediction == 1:
            status = "Visa-approved"
        else:
            status = "Visa Not-Approved"

        return templates.TemplateResponse(
            "usvisa.html",
            {"request": request, "context": status},
        )

    except Exception as e:
        return templates.TemplateResponse(
            "usvisa.html",
            {"request": request, "context": f"Error: {e}"},
        )

if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)
