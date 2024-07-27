from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from langchain_huggingface import HuggingFaceEndpoint
from langchain import PromptTemplate, LLMChain
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Get the Hugging Face API token from the environment variable
sec_key = os.getenv("HF_TOKEN")

# Define the model repository ID
repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Initialize the Hugging Face endpoint with the model ID and token
llm = HuggingFaceEndpoint(repo_id=repo_id, temperature=0.7, token=sec_key)

# Define the prompt templates
list_template = """
Question: {question}
Answer: You are a professional chef with more than 50 years of experience and specializing in saffron-based dishes. Recommend at least ten saffron-based dishes for the user's query. For each dish, include the title.
"""

detail_template =  """
Question: {dish}
Answer: You are a professional chef with more than 50 years of experience and specializing in saffron-based dishes. Provide the following details for the dish "{dish}":
1. Ingredients
2. Preparation steps
3. Tips
"""

# Create the prompt templates
list_prompt = PromptTemplate(template=list_template, input_variables=["question"])
detail_prompt = PromptTemplate(template=detail_template, input_variables=["dish"])

# Create the LLM chains with the prompt templates and LLM
list_chain = LLMChain(llm=llm, prompt=list_prompt)
detail_chain = LLMChain(llm=llm, prompt=detail_prompt)

app = FastAPI()

# Add CORS middleware to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this if your React app is served from a different origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

class DishQuery(BaseModel):
    dish: str

@app.post("/recommendations/")
async def get_recommendations(query: Query):
    response = list_chain.run(query.question)
    if response:
        dishes = response.strip().split("\n")
        return {"recommendations": dishes}
    else:
        raise HTTPException(status_code=500, detail="Error generating recommendations")

@app.post("/details/")
async def get_details(dish_query: DishQuery):
    response = detail_chain.run(dish=dish_query.dish)
    if response:
        return {"details": response}
    else:
        raise HTTPException(status_code=500, detail="Error generating details")

# uvicorn model:app --reload
