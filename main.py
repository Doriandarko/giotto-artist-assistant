import streamlit as st
import openai
import os
import json
import replicate
import traceback
from PIL import Image
import requests
import base64
from io import BytesIO

os.environ['REPLICATE_API_TOKEN'] = 'Your Key'
openai.api_key = 'Your Key'


def get_image_b64(url):
  response = requests.get(url)
  img = Image.open(BytesIO(response.content))
  buffered = BytesIO()
  img.save(buffered, format="JPEG")
  base64_img = base64.b64encode(buffered.getvalue()).decode('utf-8')
  return base64_img


def generate_image(prompt):
  final_prompt = "4k incredible quality, cinematic " + prompt
  output = replicate.run(
    "mcai/deliberate-v2:8e6663822bbbc982648e3c34214cf42d29fe421b2620cc33d8bda767fc57fe5a",
    input={"prompt": final_prompt})
  return output[0]


def transform_image(image_url, prompt, image_resolution=768):
  try:
    output = replicate.run(
      "philz1337/controlnet-deliberate:57d86bd78018d138449fda45bfcafb8b10888379a600034cc2c7186faab98c66",
      input={
        "image": image_url,
        "prompt": prompt,
        "image_resolution": str(image_resolution)
      })

    return output[1]  # Assuming that the output is an array of image URLs.
  except Exception as e:
    print("Error in transform-image:", e)
    print(traceback.format_exc())
    return {"error": "Internal Server Error"}, 500


def chat_with_assistant(messages, functions=None):
  response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613",
                                          messages=messages,
                                          functions=functions,
                                          function_call="auto")
  return response.choices[0].message


# Sidebar
st.sidebar.title('About the app')
st.sidebar.markdown("""
    This is Giotto, your helpful artist assistant. Giotto is an AI-powered app that can generate and modify images based on your inputs.
    Simply enter a prompt and let Giotto create or transform images for you. To edit an image either past a link or ask Giotto to edit a previous generated image.
    """)

st.sidebar.markdown('#### Support the project')
st.sidebar.markdown("""
    If you like this project and want to support it, please consider making a small donation.
    Every contribution helps keep the project running. Thank you!
    """)
donate_button = '[Donate](https://donate.stripe.com/fZe8AbblhbcB5XO9AA)'
st.sidebar.markdown(donate_button, unsafe_allow_html=True)

st.title('Giotto, the artist assistant')
st.subheader('Chat, generate and edit images.')

st.markdown('####\n' * 1)

if 'messages' not in st.session_state:
  st.session_state['messages'] = [{
    "role":
    "assistant",
    "content":
    "Hello! I am Giotto, your helpful artist assistant. I am named after the famous Italian painter because I excel at generating and modifying images. How can I assist you today?"
  }, {
    "role":
    "system",
    "content":
    "You are a helpful assistant which is able to generate and modify images. Your name is Giotto like the famous Italian painter. You are extremely creative, artistic, talented. Your responses should be creative and engaging. When a user asks to generate an image you improve the request by adding incredible detail to the subject and scene. If the user asks for a photo you also add the best camera setting to better capture the subject. You ask follow up question if you feel the subject is too simple and can help you create a better image. In the prompt you NEVER use words like genrate, create etc."
  }]

if 'image_prompts' not in st.session_state:
  st.session_state['image_prompts'] = {}

functions = [
  {
    "name": "generate_image",
    "description":
    "Generate an image from a prompt. If user ask for multiple images you run the fucntion more times.",
    "parameters": {
      "type": "object",
      "properties": {
        "prompt": {
          "type": "string",
          "description": "Prompt for the image generation"
        }
      },
      "required": ["prompt"],
    },
  },
  {
    "name": "transform_image",
    "description":
    "Transform an existing image. When transforming or editing the picture. Since the model takes a prompt as input it's important to keep the original subject and scene in the prompt and just edit what the user asks.Explain how you are crafting the prompt and your creative decision. just dont be too verbose.In the prompt you NEVER use words like change, transform etc.",
    "parameters": {
      "type": "object",
      "properties": {
        "image_url": {
          "type": "string",
          "description": "URL to the image file"
        },
        "prompt": {
          "type": "string",
          "description": "Prompt for the image transformation"
        },
        "image_resolution": {
          "type": "number",
          "description": "Resolution of the image"
        }
      },
      "required": ["image_url", "prompt"],
    },
  },
]

with st.form("chat_form"):
  col1, col2 = st.columns([4, 1])
  user_input = col1.text_input(
    label="Your message:",
    placeholder="What would you like to see?",
    label_visibility="collapsed",
  )
  submit_button = col2.form_submit_button("Send", use_container_width=True)

  if submit_button:
    # Start the spinner during the operation
    with st.spinner('Thinking...'):
      st.session_state.messages.append({"role": "user", "content": user_input})
      assistant_response = chat_with_assistant(st.session_state.messages,
                                               functions)
      function_args = {}

      if assistant_response.get("function_call"):
        function_name = assistant_response["function_call"]["name"]
        function_args = json.loads(
          assistant_response["function_call"]["arguments"])

        # Append assistant's response before generating image
        st.session_state.messages.append(assistant_response)

        if function_name == "generate_image":
          image_url = generate_image(function_args["prompt"])
          st.session_state['image_prompts'][str(
            image_url)] = function_args["prompt"]

        elif function_name == "transform_image":
          image_url = transform_image(
            function_args["image_url"], function_args["prompt"],
            function_args.get("image_resolution", 768))
          if isinstance(image_url, tuple) and image_url[0] == {
              "error": "Internal Server Error"
          }:
            st.error("An error occurred during image transformation.")
          else:
            st.session_state['image_prompts'][str(
              image_url)] = function_args["prompt"]

        st.session_state.messages.append({
          "role": "function",
          "name": function_name,
          "content": str(image_url)
        })

        assistant_response = chat_with_assistant(st.session_state.messages,
                                                 functions)

      else:
        st.session_state.messages.append(assistant_response)

# st.markdown('####\n' * 1)

for idx, msg in enumerate(st.session_state.messages):
  if msg["role"] == "system":
    continue  # Skip system messages in the display
  if msg["role"] == "user":
    st.markdown(
      f"<div style='color: rgb(49, 51, 63); background-color: white; padding: 20px; border: 1px solid rgba(49, 51, 63, 0.2); border-radius: 0.25rem; margin-bottom: 20px;'>{msg['content']}</div>",
      unsafe_allow_html=True)
  elif msg["role"] == "function":
    base64_img = get_image_b64(msg['content'])
    # Use the saved prompt for this image URL.
    prompt = st.session_state['image_prompts'].get(msg['content'], "")
    st.markdown(f"""
        <div style='color: rgb(49, 51, 63); background-color: mintcream; padding: 20px; border: 1px solid rgba(49, 51, 63, 0.2); border-radius: 0.25rem; margin-bottom: 20px;'>
            <img src='data:image/png;base64,{base64_img}' style='width:100%'>
            <p style='text-align: center;color: grey; margin-top: 16px;'>{prompt}</p>
        </div>
    """,
                unsafe_allow_html=True)
  else:
    if msg['content'] is not None:
      st.markdown(
        f"<div style='color: rgb(49, 51, 63); background-color: mintcream; padding: 20px; border: 1px solid rgba(49, 51, 63, 0.2); border-radius: 0.25rem; margin-bottom: 20px;'>{msg['content']}</div>",
        unsafe_allow_html=True)
    else:
      pass
