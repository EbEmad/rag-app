from fastapi import FastAPI
app=FastAPI()


@app.get('/welcome')
def welcomde():
    return {
        "message":"hello world"
    }