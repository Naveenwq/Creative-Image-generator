from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

# Your Colab ngrok URL here
COLAB_BACKEND_URL = "https://f6ba-34-73-216-6.ngrok-free.app/generate"

HTML_FORM = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SDXL Image Generator</title>
<style>
  body {
    margin: 0;
    padding: 0;
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    font-family: 'Poppins', sans-serif;
    color: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
    padding: 50px 20px;
  }

  h2 {
    font-size: 2.5rem;
    margin-bottom: 30px;
    background: linear-gradient(90deg, #00ffe5, #8a2be2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  form {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    width: 100%;
    max-width: 450px;
    margin-bottom: 30px;
    animation: fadeIn 1s ease;
  }

  label {
    font-weight: 600;
    display: block;
    margin-bottom: 8px;
    margin-top: 15px;
  }

  input[type="text"], select {
    width: 100%;
    padding: 12px;
    margin-top: 5px;
    border-radius: 12px;
    border: none;
    background: #2a2d36;
    color: white;
    font-size: 1rem;
    outline: none;
    margin-bottom: 15px;
  }

  input[type="submit"] {
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 12px;
    background: linear-gradient(90deg, #00ffe5, #8a2be2);
    color: black;
    font-weight: bold;
    font-size: 1.2rem;
    cursor: pointer;
    margin-top: 10px;
  }

  #result {
    text-align: center;
    max-width: 600px;
    animation: fadeIn 1s ease;
  }

  #generatedImage {
    max-width: 100%;
    margin-top: 20px;
    border-radius: 20px;
    display: none;
  }

  #downloadBtn {
    display: none;
    margin-top: 20px;
    padding: 10px 20px;
    background: linear-gradient(90deg, #8a2be2, #00ffe5);
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    cursor: pointer;
    font-weight: bold;
  }

  #loadingSpinner {
    display: none;
    margin-top: 30px;
  }

  .loader {
    border: 8px solid #2a2d36;
    border-top: 8px solid #00ffe5;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    animation: spin 1s linear infinite;
    margin: auto;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  @keyframes fadeIn {
    0% {opacity: 0;}
    100% {opacity: 1;}
  }
</style>
</head>
<body>

<h2>🎨 Generate Your AI Art</h2>

<form id="genForm">
  <label for="prompt">Prompt:</label>
  <input type="text" id="prompt" name="prompt" required>

  <label for="style">Style:</label>
  <select id="style" name="style">
    <option value="realistic">Realistic</option>
    <option value="digital art">Digital Art</option>
    <option value="fantasy">Fantasy</option>
    <option value="cinematic">Cinematic</option>
    <option value="painting">Painting</option>
  </select>

  <label for="resolution">Resolution:</label>
  <select id="resolution" name="resolution">
    <option value="1024x1024">1024 x 1024</option>
    <option value="768x768">768 x 768</option>
    <option value="512x512">512 x 512</option>
  </select>

  <input type="submit" value="✨ Generate">
</form>

<div id="result">
  <div id="loadingSpinner"><div class="loader"></div></div>
  <h3>Generated Image:</h3>
  <img id="generatedImage" src="" />
  <button id="downloadBtn">Download Image</button>
</div>

<script>
  const form = document.getElementById("genForm");
  const loadingSpinner = document.getElementById("loadingSpinner");
  const generatedImage = document.getElementById("generatedImage");
  const downloadBtn = document.getElementById("downloadBtn");

  form.addEventListener("submit", async function(e) {
    e.preventDefault();

    loadingSpinner.style.display = "block";
    generatedImage.style.display = "none";
    downloadBtn.style.display = "none";

    const formData = new FormData(form);

    const response = await fetch("/generate", {
      method: "POST",
      body: formData
    });

    if (response.ok) {
      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);
      generatedImage.src = imageUrl;
      generatedImage.style.display = "block";
      downloadBtn.style.display = "inline-block";

      downloadBtn.onclick = function() {
        const a = document.createElement("a");
        a.href = imageUrl;
        a.download = "generated_image.png";
        a.click();
      }
    } else {
      alert("Image generation failed. Try again!");
    }

    loadingSpinner.style.display = "none";
  });
</script>

</body>
</html>
'''

@app.get("/", response_class=HTMLResponse)
async def form():
    return HTML_FORM

@app.post("/generate")
async def generate(prompt: str = Form(...), style: str = Form(...), resolution: str = Form(...)):
    try:
        response = requests.post(
            COLAB_BACKEND_URL,
            data={"prompt": prompt, "style": style, "resolution": resolution},
            stream=True
        )
        if response.status_code != 200:
            return HTMLResponse(f"Image generation failed: {response.text}", status_code=response.status_code)

        return HTMLResponse(content=response.content, media_type="image/png")

    except Exception as e:
        return HTMLResponse(f"Request failed: {str(e)}", status_code=500)
