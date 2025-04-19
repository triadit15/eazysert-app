<!DOCTYPE html>
<html>
<head>
    <title>Verification Result</title>
</head>
<body>
    <h2>Verification Status: {{ status }}</h2>

    <h3>Extracted Text</h3>
    <pre>{{ text }}</pre>

    <h3>Processed Image</h3>
    <img src="{{ image_path }}" width="500"><br><br>

    {% if pdf_path %}
    <a href="/download_pdf?path={{ pdf_path }}">Download Certified PDF</a><br>
    {% endif %}
    <a href="/">Upload Another File</a>
</body>
</html>