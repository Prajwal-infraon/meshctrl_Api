from meshctrl_api import *
import json
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the API!"}

#Function call 
@app.get("/meshctrl")
async def meshctrl_api():
    result =check_function()
    return {"result": result}

@app.get("/add_group")
async def add_group(group_name : str =None):
    result = adddevicegroup(group_name)
    return json.loads(result)

@app.get("/general")
async def general(action : str = None):
    result = generalinfo(action)
    return json.loads(result)

@app.get("/help")
async def help_menu(help_cmd : str = None):
    result = help(help_cmd)
    return json.loads(result)

@app.get("/random_cmd")
async def random(rand : str = None):
    result = random_cmd(rand)
    return json.loads(result)

@app.get("/menu")
async def menu_bar():
    result = menu()
    return {"result":result}