from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/process_data")
async def process_data(data: dict):
    """
    This endpoint listens for HTTP POST requests at the path "/process_data".
    It expects a JSON payload containing a dictionary of data.

    Example usage:
    ```
    curl -X POST -H "Content-Type: application/json" -d '{"key": "value"}' http://localhost:8000/process_data
    ```
    """
    try:
        # Process the received data here
        # For demonstration purposes, we'll just print the data
        print("Received data:", data)
        
        # You can add your custom logic to process the data here
        
        return {"message": "Data processed successfully"}
    except Exception as e:
        # Handle exceptions appropriately based on your application needs
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application using Uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
