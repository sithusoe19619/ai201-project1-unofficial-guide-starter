"""
app.py — Gradio web interface for The Unofficial Guide.

Run:
    python app.py
"""

import gradio as gr
from generate import ask

CSS = """
.container { max-width: 780px; margin: 0 auto; padding: 0 16px; }
#title { text-align: center; padding: 24px 0 8px; }
#subtitle { text-align: center; color: #6b7280; margin-bottom: 28px; }
#ask-btn { width: 100%; margin-top: 8px; }
#answer-panel { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px 24px; margin-top: 20px; min-height: 60px; }
#sources-panel { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px 24px; margin-top: 12px; }
#sources-label { font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
"""


def handle_query(question: str):
    if not question.strip():
        return "<p style='color:#9ca3af;'>Your answer will appear here.</p>", ""

    result = ask(question)

    answer_html = result["answer"].replace("\n\n", "</p><p>").replace("\n", "<br>")
    answer_html = f"<p>{answer_html}</p>"

    sources_md = "\n".join(
        f"- [{s['name']}]({s['url']})" for s in result["sources"]
    )

    return answer_html, sources_md


with gr.Blocks(title="The Unofficial Guide") as demo:
    with gr.Column(elem_classes="container"):
        gr.HTML("<h1 id='title'>The Unofficial Guide</h1>")
        gr.HTML(
            "<p id='subtitle'>Ask anything about minimizing out-of-pocket college costs —<br>"
            "grants, work-study, SNAP, emergency funds, financial aid appeals, and more.</p>"
        )

        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g. What emergency grants exist for students facing unexpected hardship?",
            lines=2,
            show_label=True,
        )
        btn = gr.Button("Ask", variant="primary", elem_id="ask-btn")

        answer_box = gr.HTML(
            value="<p style='color:#9ca3af;'>Your answer will appear here.</p>",
            elem_id="answer-panel",
            label="Answer",
        )

        with gr.Column(elem_id="sources-panel", visible=True):
            gr.HTML("<div id='sources-label'>Sources</div>")
            sources_box = gr.Markdown(value="")

    btn.click(handle_query, inputs=inp, outputs=[answer_box, sources_box])
    inp.submit(handle_query, inputs=inp, outputs=[answer_box, sources_box])

demo.launch(css=CSS)
