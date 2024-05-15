from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

# Define the static files directory path
STATIC_PATH = "./static"

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/map")
def serve_map():
    html_file_path = os.path.join(STATIC_PATH, "index.html")
    if not os.path.exists(html_file_path):
        raise HTTPException(status_code=404, detail="Map file not found.")
    return FileResponse(html_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)