from fastapi import FastAPI, Request
from supabase import create_client, Client
import os

app = FastAPI()

# ✅ Your Supabase credentials
SUPABASE_URL = "https://xoevpqxmwajmbcbwiodp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhvZXZwcXhtd2FqbWJjYndpb2RwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU1Mzg1NTMsImV4cCI6MjA3MTExNDU1M30.szA38zDn5lcwLyjRarNO8FF-JEGcP2fElEsjML8Ynjs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Root route
@app.get("/")
def home():
    return {"message": "✅ Supabase + Render API is running!"}

# ✅ Get all rows from a table
@app.get("/data/{table}")
def get_data(table: str):
    data = supabase.table(table).select("*").execute()
    return {"data": data.data}

# ✅ Add data (POST JSON)
@app.post("/add/{table}")
async def add_data(table: str, request: Request):
    body = await request.json()
    result = supabase.table(table).insert(body).execute()
    return {"status": "ok", "inserted": result.data}

# ✅ Delete rows by filter (example)
@app.delete("/delete/{table}/{id}")
def delete_data(table: str, id: int):
    result = supabase.table(table).delete().eq("id", id).execute()
    return {"status": "deleted", "id": id}
