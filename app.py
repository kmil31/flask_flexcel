import os
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from openai import OpenAI

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = OpenAI(
    api_key=""
)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        df = pd.read_excel(filepath)

        # Convert the DataFrame to Markdown
        markdown_table = df.to_markdown(index=False)

        # Send the Markdown to OpenAI API and get the response
        ai_response = complete_table_with_ai(markdown_table)
        
        return render_template('result.html', markdown_table=ai_response)

def complete_table_with_ai(markdown_table):

    print(markdown_table)
    # Prepare the prompt for OpenAI
    prompt = f"You are an expert cybersecurity analyst who specializes in risk controls and analysis. Your primary job is asking questions to the business and assessing the evidence they provide against a cybersecurity control, and making the final decision on whether the evidence is sufficient to meet the rigorous criteria of this control. I will give you an example of a control or controls, the confirmation statement and examples of evidence, and you will determine whether the response by the business is acceptable or needs further clarification or is insufficient and raise a finding. Your input will be a markdown table that I will send after the message 'Here is your table'. Please fill in the Findings column of the table, and then return the completed table in Markdown format. ONLY return the table, do not yap and add any unnecessary responses.Only elaborate in the Findings column why you think the evidence is insufficient to meet the control. Here is your table:{markdown_table}"
    
    print(prompt)
    # Send the request to OpenAI and get the response
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    # Extract the response text
    ai_completed_table = completion.choices[0].message.content
    
    return ai_completed_table

if __name__ == '__main__':
    app.run(debug=True)
