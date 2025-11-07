from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from workflow import GTMAutomationWorkflow
from trends_analyzer import TrendsAnalyzer
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/gtm")
def start():
    try:
      GTM = GTMAutomationWorkflow()
      result=GTM.run(False)
      return {"status": "started", "result": result}
    except Exception as e:
        return {"error":str(e)}
@app.post("/gtm_week")
def start():
    try:
      Trend = TrendsAnalyzer()
      result=Trend.run()
      return {"result": result}
    except Exception as e:
        return {"error":str(e)}
