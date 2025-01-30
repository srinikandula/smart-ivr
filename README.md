# IVR AI Assistant

This Python application integrates Twilio's voice capabilities with OpenAI's language model to create an Interactive Voice Response (IVR) system. The system can handle customer queries related to logistics, such as shipment tracking and delivery status, using voice interactions.

## Features

- Initiates phone calls using Twilio.
- Processes user speech input and generates responses using OpenAI's GPT-3.5-turbo model.
- Provides a conversational interface for user queries through voice.
- Supports retries for processing user input in case of errors.

## Requirements

- Python 3.x
- Libraries:
  - `Flask`
  - `openai`
  - `twilio`
  - `python-dotenv`

You can install the required libraries using pip


## Environment Variables

Before running the application, ensure that the following environment variables are set in a `.env` file:

| Variable          | Description        |
|-------------------|--------------------|
| `TWILIO_SID`         | Twilio SID         |
| `TWILIO_AUTH_TOKEN`         | Twilio AuthToken   |
| `TWILIO_PHONE_NUMBER`         | Twilio Phonenumber |
| `OPENAI_API_KEY`     | OpenAI API Key     |


## Usage

1. **Run the Application**: Start the Flask server by executing the following command in your terminal:


2. **Trigger an IVR Call**: Send a POST request to `/trigger_ivr` with a JSON payload containing the mobile number:

```json
{
"mobileNumber": "<recipient_mobile_number>"
}
```
```bash
curl -X POST http://localhost:5000/trigger_ivr -H "Content-Type: application/json" -d '{"mobileNumber": "+1234567890"}'
```

3. **Interact with the IVR**: Once the call is initiated, the recipient will hear a greeting and can respond with their queries. The AI will process their speech and respond accordingly.

## Endpoints

### `/trigger_ivr`

- **Method**: POST
- **Description**: Initiates an IVR call to the specified mobile number.
- **Request Body**:
- `mobileNumber`: The phone number to call (required).

### `/ivr`

- **Method**: POST
- **Description**: Handles the initial IVR interaction, greeting the user and gathering their input.

### `/process_audio`

- **Method**: POST
- **Description**: Processes the recognized speech from the user, generates an AI response, and continues the conversation.

### `/ping`

- **Method**: GET
- **Description**: A simple health check endpoint to confirm that the server is running.

## Error Handling

The application includes error handling for both Twilio and OpenAI API calls. If there are issues processing user input, it will retry up to three times before returning an error message.
