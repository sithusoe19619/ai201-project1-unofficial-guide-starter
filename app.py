"""
app.py — Gradio web interface for The Unofficial Guide.

Run:
    python app.py
"""

import gradio as gr
from generate import ask


def handle_query(question: str):
    if not question.strip():
        return "", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown(
        "## The Unofficial Guide\n"
        "Ask anything about minimizing out-of-pocket college costs — "
        "grants, work-study, SNAP, emergency funds, financial aid appeals, and more."
    )
    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. How do I apply for a Pell Grant?",
        lines=2,
    )
    btn = gr.Button("Ask", variant="primary")
    answer_box = gr.Textbox(label="Answer", lines=10)
    sources_box = gr.Textbox(label="Sources retrieved", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer_box, sources_box])
    inp.submit(handle_query, inputs=inp, outputs=[answer_box, sources_box])

demo.launch()
