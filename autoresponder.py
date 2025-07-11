import azure.functions as func
import logging
import json
import os
import urllib.request
import urllib.parse

# Azure Functions Code
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="autoresponder_parser", methods=["POST"])
def autoresponder_parser(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Autoresponder parser function processed a request.')
    
    try:
        # Extract the request body
        req_body = req.get_json()
        if not req_body or 'text' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'text' field in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        body_text = req_body['text']
        
        # Get OpenAI API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return func.HttpResponse(
                json.dumps({"error": "OpenAI API key not configured"}),
                status_code=500,
                mimetype="application/json"
            )
        
        # Create the prompt for OpenAI
        system_prompt = """You are an AI assistant that classifies travel business enquiries. 
        
        Classification rules:
        1 = Tours: enquiry about tour availability or pricing to a specific place
        2 = Vehicle: enquiry about specific vehicle type availability or rental pricing
        3 = Human needed: Generic enquiry, related to travel perhaps, but not directly to our business. OR, if user is frustrated or needs explicit help.
        4 = Other: totally unrelated queries.
        
        For case 1: extract city_name
        For case 2: extract vehicle_name
        For cases 3,4: leave parameters blank
        
        Respond ONLY with valid JSON in this exact format:
        {
            "case": <number>,
            "params": {
                "city_name": "<city_name or empty string>",
                "vehicle_name": "<vehicle_name or empty string>"
            }
        }"""
        
        user_prompt = f"Classify this travel enquiry: {body_text}"
        
        # Prepare the request payload for OpenAI API
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 200,
            "temperature": 0.1
        }
        
        # Convert payload to JSON
        data = json.dumps(payload).encode('utf-8')
        
        # Create the HTTP request
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {openai_api_key}'
        }
        
        # Make the request to OpenAI API
        request = urllib.request.Request(url, data=data, headers=headers)
        
        try:
            with urllib.request.urlopen(request) as response:
                response_data = response.read().decode('utf-8')
                openai_response = json.loads(response_data)
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            logging.error(f"OpenAI API error: {e.code} - {error_body}")
            return func.HttpResponse(
                json.dumps({"error": f"OpenAI API error: {e.code}"}),
                status_code=500,
                mimetype="application/json"
            )
        except Exception as e:
            logging.error(f"Request error: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to call OpenAI API"}),
                status_code=500,
                mimetype="application/json"
            )
        
        # Extract the response content
        try:
            gpt_response = openai_response['choices'][0]['message']['content'].strip()
            
            # Try to parse the JSON response
            result = json.loads(gpt_response)
            
            # Validate the response format
            if not isinstance(result, dict) or "case" not in result or "params" not in result:
                raise ValueError("Invalid response format")
            
            # Ensure case is an integer between 1-5
            case_value = result["case"]
            if not isinstance(case_value, int) or case_value < 1 or case_value > 5:
                raise ValueError("Invalid case value")
            
            # Ensure params structure is correct
            params = result["params"]
            if not isinstance(params, dict):
                raise ValueError("Invalid params format")
            
            # Ensure required fields exist in params
            if "city_name" not in params:
                params["city_name"] = ""
            if "vehicle_name" not in params:
                params["vehicle_name"] = ""
            
            # Clean up parameters based on case
            if case_value == 1:
                params["vehicle_name"] = ""
            elif case_value == 2:
                params["city_name"] = ""
            elif case_value in [3, 4]:
                params["city_name"] = ""
                params["vehicle_name"] = ""
            
            # Return the structured response
            return func.HttpResponse(
                json.dumps(result),
                status_code=200,
                mimetype="application/json"
            )
            
        except json.JSONDecodeError:
            logging.error(f"Failed to parse GPT response as JSON: {gpt_response}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to parse AI response"}),
                status_code=500,
                mimetype="application/json"
            )
        except ValueError as e:
            logging.error(f"Invalid response format: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Invalid AI response format"}),
                status_code=500,
                mimetype="application/json"
            )
        except KeyError as e:
            logging.error(f"Missing key in OpenAI response: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Invalid OpenAI response structure"}),
                status_code=500,
                mimetype="application/json"
            )
            
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )
