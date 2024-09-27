import gradio as gr
from urllib.parse import urlparse
import requests
import time
import os

from utils.gradio_helpers import parse_outputs, process_outputs

names = ['image', 'rotate_pitch', 'rotate_yaw', 'rotate_roll', 'blink', 'eyebrow', 'wink', 'pupil_x', 'pupil_y', 'aaa', 'eee', 'woo', 'smile', 'src_ratio', 'sample_ratio', 'crop_factor', 'output_format', 'output_quality']

def predict(request: gr.Request, *args, progress=gr.Progress(track_tqdm=True)):
    headers = {'Content-Type': 'application/json'}

    payload = {"input": {}}
    
    
    base_url = "http://0.0.0.0:7860"
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
        
        return tuple(processed_outputs) if len(processed_outputs) > 1 else processed_outputs[0]
    else:
        if(response.status_code == 409):
            raise gr.Error(f"Sorry, the Cog image is still processing. Try again in a bit.")
        raise gr.Error(f"The submission failed! Error: {response.status_code}")



with gr.Blocks() as demo:
    with gr.Column():
        gr.Markdown("# Expression Editor")
        gr.Markdown("Demo for expression-editor cog image by fofr")
        with gr.Row():
            with gr.Column():
                image = gr.Image(
                    label="Image", 
                    type="filepath"
                )
                with gr.Row():
                    rotate_pitch = gr.Slider(
                        label="Rotate Pitch", info='''Rotation pitch: Adjusts the up and down tilt of the face''', 
                        value=0,
                        minimum=-20, maximum=20
                    )
                    rotate_yaw = gr.Slider(
                        label="Rotate Yaw", info='''Rotation yaw: Adjusts the left and right turn of the face''', 
                        value=0,
                        minimum=-20, maximum=20
                    )
                    rotate_roll = gr.Slider(
                        label="Rotate Roll", info='''Rotation roll: Adjusts the tilt of the face to the left or right''', value=0,
                        minimum=-20, maximum=20
                    )
                with gr.Row():
                    blink = gr.Slider(
                        label="Blink", info='''Blink: Controls the degree of eye closure''', value=0,
                        minimum=-20, maximum=5
                    )
                    eyebrow = gr.Slider(
                        label="Eyebrow", info='''Eyebrow: Adjusts the height and shape of the eyebrows''', value=0,
                        minimum=-10, maximum=15
                    )
                    wink = gr.Number(
                        label="Wink", info='''Wink: Controls the degree of one eye closing''', value=0
                    )
                with gr.Row():
                    pupil_x = gr.Slider(
                        label="Pupil X", info='''Pupil X: Adjusts the horizontal position of the pupils''', value=0,
                        minimum=-15, maximum=15
                    )
                    pupil_y = gr.Slider(
                        label="Pupil Y", info='''Pupil Y: Adjusts the vertical position of the pupils''', value=0,
                        minimum=-15, maximum=15
                    )
                with gr.Row():
                    aaa = gr.Slider(
                        label="Aaa", info='''AAA: Controls the mouth opening for 'aaa' sound''', value=0,
                        minimum=-30, maximum=120
                    )
                    eee = gr.Slider(
                        label="Eee", info='''EEE: Controls the mouth shape for 'eee' sound''', value=0,
                        minimum=-20, maximum=15
                    )
                    woo = gr.Slider(
                        label="Woo", info='''WOO: Controls the mouth shape for 'woo' sound''', value=0,
                        minimum=-20, maximum=15
                    )
                smile = gr.Slider(
                    label="Smile", info='''Smile: Adjusts the degree of smiling''', value=0,
                    minimum=-0.3, maximum=1.3
                )
                with gr.Accordion("More Settings", open=False):
                    src_ratio = gr.Number(
                        label="Src Ratio", info='''Source ratio''', value=1
                    )
                    sample_ratio = gr.Slider(
                        label="Sample Ratio", info='''Sample ratio''', value=1,
                        minimum=-0.2, maximum=1.2
                    )
                    crop_factor = gr.Slider(
                        label="Crop Factor", info='''Crop factor''', value=1.7,
                        minimum=1.5, maximum=2.5
                    )
                    output_format = gr.Dropdown(
                        choices=['webp', 'jpg', 'png'], label="output_format", info='''Format of the output images''', value="webp"
                    )
                    output_quality = gr.Number(
                        label="Output Quality", info='''Quality of the output images, from 0 to 100. 100 is best quality, 0 is lowest quality.''', value=95
                    )
                submit_btn = gr.Button("Submit")
            with gr.Column():
                result_image = gr.Image()

    inputs = [image, rotate_pitch, rotate_yaw, rotate_roll, blink, eyebrow, wink, pupil_x, pupil_y, aaa, eee, woo, smile, src_ratio, sample_ratio, crop_factor, output_format, output_quality]
    outputs = [result_image]

    submit_btn.click(
        fn=predict,
        inputs=inputs,
        outputs=outputs,
    )

    rotate_pitch.release(fn=predict, inputs=inputs, outputs=outputs)
    rotate_yaw.release(fn=predict, inputs=inputs, outputs=outputs)
    rotate_roll.release(fn=predict, inputs=inputs, outputs=outputs)
    blink.release(fn=predict, inputs=inputs, outputs=outputs)
    eyebrow.release(fn=predict, inputs=inputs, outputs=outputs)
    wink.release(fn=predict, inputs=inputs, outputs=outputs)
    pupil_x.release(fn=predict, inputs=inputs, outputs=outputs)
    pupil_y.release(fn=predict, inputs=inputs, outputs=outputs)
    aaa.release(fn=predict, inputs=inputs, outputs=outputs)
    eee.release(fn=predict, inputs=inputs, outputs=outputs)
    woo.release(fn=predict, inputs=inputs, outputs=outputs)
    smile.release(fn=predict, inputs=inputs, outputs=outputs)

demo.launch(share=False, show_error=True)

