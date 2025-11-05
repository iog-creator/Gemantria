import os

from src.services.inference_client import InferenceClient

try:

    from src.utils.math_clean import extract_number

except Exception:

    def extract_number(t): return t[:64]

c = InferenceClient()

def ask(model, prompt, numeric=False):

    r=c.chat_completions(model=model, messages=[{"role":"user","content":prompt}], max_tokens=64, temperature=0.2)

    out = r.get("choices",[{}])[0].get("message",{}).get("content","")

    print(f"HINT:model={model}")

    print("HINT:text=", extract_number(out) if numeric else out[:180])

ask(os.environ["THEOLOGY_MODEL"], "Define 'covenant' in Genesis in one sentence.")

ask(os.environ["MATH_MODEL"], "Compute: (37^2 - 13^2) / 12. Return only a number.", numeric=True)
