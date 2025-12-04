import json
import re
import logging

# The failing text from the log
failing_text = r"""{"meta":[{"title":"Fine Tune GPT-OSS Model with Your Own Text Files: Beginner’s Guide","level":"beginner"}],"sections":[{"name":"Introduction","content":["Unlock the power of GPT‑OSS for your own data—no expert knowledge needed!","In this guide you will learn how to fine‑tune a large language model with just a few text files.","We will cover data preparation, environment setup, training, evaluation, and deployment, all using beginner‑friendly tools."]},{"name":"Prerequisites","content":["Python 3.9 or newer","pip (Python package installer)","Git for version control","Jupyter Notebook for interactive coding","PyTorch for model execution"]},{"name":"Environment Setup","content":["Create a new Python virtual environment: `python -m venv gpt_oss_env`","Activate it: `source gpt_oss_env/bin/activate` on macOS/Linux or `.\gpt_oss_env\\Scripts\\activate` on Windows","Upgrade pip: `pip install --upgrade pip`","Clone the GPT‑OSS repository: `git clone https://github.com/openai/gpt-oss.git`","Navigate into the repo: `cd gpt-oss`","Install required packages: `pip install -r requirements.txt`"]},{"name":"Data Requirements","content":["Prepare plain text files (.txt) with your domain‑specific content","Each file should contain coherent passages, preferably between 100–200 words","Avoid extremely long documents; split them into smaller chunks for better learning"]},{"name":"Data Preparation","content":["Clean text: remove non‑ASCII characters, fix encoding issues","Tokenize text using GPT‑OSS tokenizer (included in repo)","Create a JSONL file where each line is a training example: `{\"text\": \"Your text here.\"}`","Shuffle the dataset to ensure randomization","Split into training and validation sets (e.g., 90% train, 10% validation)"]},{"name":"Configuration of Fine‑Tuning","content":["Open the `config.yaml` template in the repository","Set `train_file` and `validation_file` paths to your JSONL files","Adjust hyperparameters: learning rate (e.g., 5e-5), batch size (e.g., 8), number of epochs (e.g., 3)","Optionally enable mixed‑precision training for faster execution"]},{"name":"Executing Fine‑Tuning","content":["Launch the training script: `python train.py --config config.yaml`","Monitor GPU usage and training loss via the console or TensorBoard","Training logs will show loss decreasing and validation perplexity improving","Training may take from a few minutes to several hours depending on hardware"]},{"name":"Model Evaluation","content":["Load the best checkpoint from the training run","Generate sample outputs using the command: `python generate.py --prompt \"Your prompt here.\" --model_dir ./checkpoints`","Compute perplexity on the validation set with `python evaluate.py`","Assess qualitative quality by reviewing generated text for relevance and coherence"]},{"name":"Iterative Improvement","content":["If performance is unsatisfactory, try increasing dataset size or adding more diverse examples","Experiment with different learning rates, batch sizes, or number of epochs","Re‑run training with updated settings","Repeat evaluation until desired quality is achieved"]},{"name":"Local Deployment","content":["Export the fine‑tuned model to ONNX or TorchScript if needed","Create a simple inference script using PyTorch: load the model, tokenize input, generate output","Integrate into a Jupyter Notebook or a lightweight Flask app for real‑time usage","Ensure the environment has the same dependencies installed for consistency"]}]}"""


def fix_invalid_escapes(text):
    # Match double backslashes (keep them) OR single backslashes not followed by valid escape chars (escape them)
    return re.sub(
        r'(\\\\)|(\\(?!["\\/bfnrtu]))',
        lambda m: m.group(1) if m.group(1) else r"\\",
        text,
    )


def safe_json_loads(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Initial load failed: {e}")

        # Try fixing escapes
        fixed_text = fix_invalid_escapes(text)
        try:
            return json.loads(fixed_text)
        except json.JSONDecodeError as e2:
            print(f"Load after fix failed: {e2}")
            return None


print("Testing safe_json_loads with failing text...")
result = safe_json_loads(failing_text)
if result:
    print("SUCCESS: JSON parsed successfully after fix.")
    # print(json.dumps(result, indent=2))
else:
    print("FAILURE: Could not parse JSON.")
