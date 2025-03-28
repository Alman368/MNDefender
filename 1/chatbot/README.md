# Flask REST API

This project is a simple Flask REST API that receives a text input and returns a random message. 

## Project Structure

```
chatbot
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── controllers
│   │   └── message_controller.py
│   └── services
│       └── message_service.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd chatbot
   ```

2. Install the required packages:
   ```
   pip install -r app/requirements.txt
   ```

## Usage

1. Run the application:
   ```
   flask --app app/main run --host=0.0.0.0
   ```

2. Send a POST request to the `/send-message` endpoint with a JSON body containing the text input:
   ```json
   {
       "message": "Your input text here"
   }
   ```

3. The API will respond with a random message based on the input.
   ```json
   {
       "message": "Response here"
   }
   ```

## Endpoints

- **POST /send-message**: Receives text input and returns a random message.

## Usage with Docker

The application can also be run in a Docker container without the need to install anything on the host machine.

1. Run the following command to run the application in a Docker container:
   ```
   docker-compose up
   ```

## License

This project is licensed under the MIT License.
