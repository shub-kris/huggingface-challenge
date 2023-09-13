import ast
import json

import gradio as gr
from sagemaker.predictor import Predictor

## Deployed Endpoint
endpoint = "bert-qa-dem-d01b00d6-9bf6-43d2-be4d-d17-2023-09-12-19-37-06-052"
predictor = Predictor(endpoint)


def get_prediction(context, question):
    payload = {"inputs": {"question": question, "context": context}}
    inference_response = predictor.predict(
        data=json.dumps(payload), initial_args={"ContentType": "application/json"}
    )
    answer_dict = ast.literal_eval(inference_response.decode())
    return [answer_dict["answer"], answer_dict["score"]]


demo = gr.Interface(
    fn=get_prediction,
    inputs=[
        gr.inputs.Textbox(
            default="My name is Shubham Krishna. I come from India. I am a ML Engineer with expertise in NLP and would like to work for HuggingFace.",
            label="Context Paragraph",
        ),
        gr.inputs.Textbox(
            default="Which company would Shubham like to work for?", label="Question"
        ),
    ],
    outputs=[
        gr.outputs.Textbox(label="Answer"),
        gr.outputs.Textbox(label="Confidence in Answer"),
    ],
    title="Q&A App",
    allow_flagging="never",
)

if __name__ == "__main__":
    demo.launch(server_port=80, share=False)
