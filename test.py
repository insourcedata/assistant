from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from studynote.chain import convert_bookmarksstr_to_list, chain_invoke

app = FastAPI(
    title="StudyNote Assistant",
    version="v0.1",
    description="A simple api server to process bookmarks",
)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/process")
async def process_data(
        param1: str = Form(...),         
        file: UploadFile = File(...)
    ):
    
    data = await file.read()
    bookmarks_str = data.decode('utf-8')
    bookmarks = convert_bookmarksstr_to_list(bookmarks_str)

    # Call the function from chain.py and get the path of the generated Markdown file
    md_file_path = chain_invoke(param1, bookmarks)

    # Return the Markdown file as a download
    return FileResponse(md_file_path, media_type='text/markdown', filename="output.md")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
