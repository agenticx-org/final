import pytest
import asyncio
import websockets
import json
import os

@pytest.mark.asyncio
async def test_websocket_request_response():
    # Get the websocket URL from environment or use default
    ws_url = os.getenv('WEBSOCKET_URL', 'ws://localhost:8000/ws')
    print(f"\nConnecting to websocket at: {ws_url}")
    
    async with websockets.connect(ws_url) as websocket:
        # Prepare the request message
        request = {
            "type": "request",
            "project_id": "123",
            "content": "Write me a report in markdown showing the top 5 and bottom five selling cars in the world."
        }
        
        # Send the message
        await websocket.send(json.dumps(request))
        print(f"\nSent message: {json.dumps(request, indent=2)}")
        
        # Set up a timeout for receiving messages
        try:
            while True:
                # Wait for response with timeout
                response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                print(f"\nReceived response: {response}")
                
                # Parse the response
                response_data = json.loads(response)
                
                # If we receive a completion message, break the loop
                if response_data.get("type") == "completion":
                    break
                
        except asyncio.TimeoutError:
            print("\nTimeout waiting for response after 30 seconds")
            raise
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            raise
