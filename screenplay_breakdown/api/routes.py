# FastAPI router for script ingestion endpoints
# POST /upload — accept a screenplay file (txt, pdf, fdx)
#   read file contents
#   detect file type and route to correct parser
#   return list of parsed scenes as JSON
# POST /paste — accept raw screenplay text as string
#   pass directly to text_parser.py
#   return list of parsed scenes as JSON

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os

from screenplay_breakdown.services.pipeline_service import process_pdf_to_excel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/process-script")
async def process_script(file: UploadFile = File(...)):
    print("API received file:", file.filename)
    pdf_path = os.path.join(UPLOAD_DIR, file.filename)

    # save uploaded file
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # run pipeline
    output_path = process_pdf_to_excel(pdf_path)

    # return Excel file
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="shot_breakdown.xlsx"
    )