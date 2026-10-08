import gradio as gr
from main import app as fastapi_app

# Sederhana: Tampilan status antarmuka di root /
with gr.Blocks(title="Tubi Backend API") as demo:
    gr.Markdown("# 🚀 Tubi Media Backend is Running")
    gr.Markdown("Backend FastAPI aktif dan melayani permintaan dari Tubi Frontend di Vercel.")
    gr.Markdown("- Endpoint Info: `/api/info`")
    gr.Markdown("- Endpoint Download: `/api/download`")
    gr.Markdown("- Status: Healthy")

# Mount Gradio app ke FastAPI
app = gr.mount_gradio_app(fastapi_app, demo, path="/")
