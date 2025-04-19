idef add_certification_stamp(image_path):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Choose font — fallback to default if truetype fails
    try:
        font = ImageFont.truetype("arial.ttf", 28) # You can adjust the font size here
    except:
        font = ImageFont.load_default()

    # Define stamp content
    stamp_text = f"CERTIFIED BY EAZY CERT\n{datetime.datetime.now().strftime('%Y-%m-%d')}"

    # Position and appearance
    x, y = 50, 50
    text_color = "red"
    border_color = "black"

    # Optional: Draw a border rectangle for the stamp
    text_size = draw.multiline_textsize(stamp_text, font=font)
    padding = 20
    draw.rectangle(
        [x - padding, y - padding, x + text_size[0] + padding, y + text_size[1] + padding],
        outline=border_color,
        width=3
    )

    # Draw the stamp text
    draw.multiline_text((x, y), stamp_text, fill=text_color, font=font)

    # Save
    certified_path = image_path.replace(".jpg", "_certified.jpg")
    image.save(certified_path)
    return certified_path