# FastAPI router for script ingestion endpoints
# POST /upload — accept a screenplay file (txt, pdf, fdx)
#   read file contents
#   detect file type and route to correct parser
#   return list of parsed scenes as JSON
# POST /paste — accept raw screenplay text as string
#   pass directly to text_parser.py
#   return list of parsed scenes as JSON