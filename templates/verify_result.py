<!doctype html>
<html>
<head>
    <title>Verification Result</title>
</head>
<body>
    <h1>{{ result }}</h1>

    <h3>Certified Document Preview:</h3>
    <img src="{{ url_for('static', filename=image_path) }}" width="500"><br><br>

    <a href="{{ url_for('download_file', filename=image_path) }}">
        <button>Download Certified Image</button>
    </a><br><br>

    <a href="/">Verify Another</a>
</body>
</html>