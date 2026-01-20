async function uploadImage() {
    const fileInput = document.getElementById("imageInput");

    if (fileInput.files.length === 0) {
        alert("Please select an image");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch("http://127.0.0.1:8000/process-image", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    document.getElementById("result").innerHTML = `
        <h3>Detected Ingredients:</h3>
        <pre>${JSON.stringify(data.predictions, null, 2)}</pre>

        <h3>Extracted Text (OCR):</h3>
        <p>${data.ocr_text}</p>
    `;
}

