import gradio as gr
from urllib.parse import urlparse
import requests
import time
import os

from utils.gradio_helpers import parse_outputs, process_outputs

inputs = []
inputs.append(gr.Image(
    label="Image", type="filepath"
))

inputs.append(gr.Slider(
    label="Rotate Pitch", info='''Rotation pitch: Adjusts the up and down tilt of the face''', value=0,
    minimum=-20, maximum=20
))

inputs.append(gr.Slider(
    label="Rotate Yaw", info='''Rotation yaw: Adjusts the left and right turn of the face''', value=0,
    minimum=-20, maximum=20
))

inputs.append(gr.Slider(
    label="Rotate Roll", info='''Rotation roll: Adjusts the tilt of the face to the left or right''', value=0,
    minimum=-20, maximum=20
))

inputs.append(gr.Slider(
    label="Blink", info='''Blink: Controls the degree of eye closure''', value=0,
    minimum=-20, maximum=5
))

inputs.append(gr.Slider(
    label="Eyebrow", info='''Eyebrow: Adjusts the height and shape of the eyebrows''', value=0,
    minimum=-10, maximum=15
))

inputs.append(gr.Number(
    label="Wink", info='''Wink: Controls the degree of one eye closing''', value=0
))

inputs.append(gr.Slider(
    label="Pupil X", info='''Pupil X: Adjusts the horizontal position of the pupils''', value=0,
    minimum=-15, maximum=15
))

inputs.append(gr.Slider(
    label="Pupil Y", info='''Pupil Y: Adjusts the vertical position of the pupils''', value=0,
    minimum=-15, maximum=15
))

inputs.append(gr.Slider(
    label="Aaa", info='''AAA: Controls the mouth opening for 'aaa' sound''', value=0,
    minimum=-30, maximum=120
))

inputs.append(gr.Slider(
    label="Eee", info='''EEE: Controls the mouth shape for 'eee' sound''', value=0,
    minimum=-20, maximum=15
))

inputs.append(gr.Slider(
    label="Woo", info='''WOO: Controls the mouth shape for 'woo' sound''', value=0,
    minimum=-20, maximum=15
))

inputs.append(gr.Slider(
    label="Smile", info='''Smile: Adjusts the degree of smiling''', value=0,
    minimum=-0.3, maximum=1.3
))

inputs.append(gr.Number(
    label="Src Ratio", info='''Source ratio''', value=1
))

inputs.append(gr.Slider(
    label="Sample Ratio", info='''Sample ratio''', value=1,
    minimum=-0.2, maximum=1.2
))

inputs.append(gr.Slider(
    label="Crop Factor", info='''Crop factor''', value=1.7,
    minimum=1.5, maximum=2.5
))

inputs.append(gr.Dropdown(
    choices=['webp', 'jpg', 'png'], label="output_format", info='''Format of the output images''', value="webp"
))

inputs.append(gr.Number(
    label="Output Quality", info='''Quality of the output images, from 0 to 100. 100 is best quality, 0 is lowest quality.''', value=95
))

names = ['image', 'rotate_pitch', 'rotate_yaw', 'rotate_roll', 'blink', 'eyebrow', 'wink', 'pupil_x', 'pupil_y', 'aaa', 'eee', 'woo', 'smile', 'src_ratio', 'sample_ratio', 'crop_factor', 'output_format', 'output_quality']

outputs = []
outputs.append(gr.Image())

expected_outputs = len(outputs)
def predict(request: gr.Request, *args, progress=gr.Progress(track_tqdm=True)):
    headers = {'Content-Type': 'application/json'}

    payload = {"input": {}}
    
    
    parsed_url = urlparse(str(request.url))
    base_url = parsed_url.scheme + "://" + parsed_url.netloc
    for i, key in enumerate(names):
        value = args[i]
        if value and (os.path.exists(str(value))):
            value = f"{base_url}/file=" + value
        if value is not None and value != "":
            payload["input"][key] = value

    response = requests.post("http://0.0.0.0:5000/predictions", headers=headers, json=payload)

    
    if response.status_code == 201:
        follow_up_url = response.json()["urls"]["get"]
        response = requests.get(follow_up_url, headers=headers)
        while response.json()["status"] != "succeeded":
            if response.json()["status"] == "failed":
                raise gr.Error("The submission failed!")
            response = requests.get(follow_up_url, headers=headers)
            time.sleep(1)
    if response.status_code == 200:
        json_response = response.json()
        #If the output component is JSON return the entire output response 
        if(outputs[0].get_config()["name"] == "json"):
            return json_response["output"]
        predict_outputs = parse_outputs(json_response["output"])
        processed_outputs = process_outputs(predict_outputs)
        difference_outputs = expected_outputs - len(processed_outputs)
        # If less outputs than expected, hide the extra ones
        if difference_outputs > 0:
            extra_outputs = [gr.update(visible=False)] * difference_outputs
            processed_outputs.extend(extra_outputs)
        # If more outputs than expected, cap the outputs to the expected number
        elif difference_outputs < 0:
            processed_outputs = processed_outputs[:difference_outputs]
        
        return tuple(processed_outputs) if len(processed_outputs) > 1 else processed_outputs[0]
    else:
        if(response.status_code == 409):
            raise gr.Error(f"Sorry, the Cog image is still processing. Try again in a bit.")
        raise gr.Error(f"The submission failed! Error: {response.status_code}")

title = "Demo for expression-editor cog image by fofr"
model_description = "None"

app = gr.Interface(
    fn=predict,
    inputs=inputs,
    outputs=outputs,
    title=title,
    description=model_description,
    allow_flagging="never",
)
app.launch(share=False, show_error=True)

