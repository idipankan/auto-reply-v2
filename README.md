## Overview

**auto-reply-v2** is an AI-powered email agent designed for travel businesses. It automatically processes incoming customer emails, classifies their intent using OpenAI's GPT-4, queries a SQL database for relevant information, and sends personalized responses. The solution leverages Azure Functions, Azure Logic Apps, and integrates with Gmail and SQL databases for seamless automation.

## Features

- **AI-Powered Classification:** Uses OpenAI GPT-4 to classify email intent (tour inquiry, vehicle rental, human intervention, or unrelated).
- **Context Extraction:** Extracts key parameters (city name, vehicle type) from unstructured email text.
- **Database Query:** Fetches relevant data (tour availability, vehicle rates) from a SQL database.
- **Dynamic Email Responses:** Crafts and sends context-aware replies to customers via Gmail.
- **Escalation Handling:** Routes complex or unrelated queries to human agents or provides appropriate fallback responses.
- **Azure Native:** Built using Azure Functions and Logic Apps for scalability and easy integration.

## Architecture & Workflow

![Solution flow](https://i.ibb.co/gLY961st/Flow-v2.png)

### Detailed Steps
1. **Trigger:** Logic App monitors Gmail inbox for new emails.
2. **Preprocessing:** Cleanses the email body to remove quoted text.
3. **Classification:** Sends the cleansed text to the Azure Function (`autoresponder_parser`), which calls OpenAI GPT-4 to classify the query and extract parameters.
4. **Parameter Extraction:** Receives structured JSON with case type and extracted parameters (city/vehicle).
5. **Database Query:** Depending on the case, queries the SQL database for tours or vehicles.
6. **Response Generation:** Crafts a personalized reply based on the query result and sends it via Gmail.
7. **Escalation/Fallback:** For generic or unrelated queries, escalates to a human or sends a fallback response.

## Setup & Deployment

### Prerequisites
- Azure Subscription
- OpenAI API Key
- Azure Function App
- Azure Logic App
- SQL Database with `Tours` and `Vehicles` tables
- Gmail account (API connection)

### Configuration
1. **Azure Function:**
   - Deploy `autoresponder.py` as an HTTP-triggered Azure Function.
   - Set the `OPENAI_API_KEY` environment variable.
2. **Logic App:**
   - Import `logic-app.json` into Azure Logic Apps Designer.
   - Configure connections for Gmail and SQL.
   - Update the HTTP action URL to point to your deployed Azure Function endpoint.
3. **Database:**
   - Ensure your SQL database has the required tables and data:
     - `Tours(TOUR_NAME, Price, ...)`
     - `Vehicles(VEHICLE_NAME, Rate, ...)`

### Running Locally (for Function)
- Install dependencies: `pip install azure-functions`
- Set environment variable: `OPENAI_API_KEY=<your-openai-key>`
- Run locally with Azure Functions Core Tools or deploy to Azure.

## Usage
- Once deployed, the system will automatically respond to new emails in the configured Gmail inbox.
- Responses are tailored based on the detected intent and available data.
- Escalations and fallback responses are handled automatically.

## Customization
- Update the OpenAI prompt in `autoresponder.py` to refine classification rules.
- Modify SQL queries in `logic-app.json` to match your schema.
- Adjust email templates in Logic App actions for branding.
