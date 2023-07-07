# Giotto, The Artist Assistant

Giotto is a creative, artistic, and talented assistant, named after the famous Italian painter Giotto di Bondone. It leverages the power of AI to generate and modify images based on user input. Giotto employs the OpenAI GPT-3.5 Turbo model for conversational AI and Replicate for image generation and modification.

## Requirements

This project requires:

- Python 3.7+
- Streamlit 1.0.0+
- OpenAI API key
- Replicate API key
- PIL (Pillow)
- Requests

All required Python libraries are listed in `requirements.txt`.

## Installation

1. Clone this repository to your local machine.

2. Install the required Python packages using the following command:
```shell
pip install openai replicate
```

3. Set your environment variables for the OpenAI API key and Replicate API token:

```shell
export OPENAI_API_KEY="your-openai-api-key"
export REPLICATE_API_TOKEN="your-replicate-api-token"
```

Alternatively, you can replace the placeholders directly in the script. However, it's generally safer to use environment variables to protect your keys.

## Usage

After setting up, you can run Giotto using Streamlit with the following command:

```shell
streamlit run giotto.py
```

This will open a new browser window or tab with the Giotto application.

### Features

- Chat with Giotto: Send text input to Giotto and receive creative and engaging responses.
- Generate Images: Ask Giotto to generate images based on a text prompt. The generated images are displayed in the chat.
- Transform Images: Provide an image URL and a transformation prompt, and Giotto will modify the image accordingly.

## Support

If you like this project and want to support it, please consider making a small donation. Every contribution helps keep the project running. You can donate through the button at the bottom of the application. Thank you!

## Note

The code for Giotto is made for demonstrative purposes and is not meant for production use. The API keys are hardcoded and need to be replaced with your own API keys. Always be sure to keep your keys secure.

## License

This project is licensed under the terms of the MIT license.