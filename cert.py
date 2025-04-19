def add_certification_stamp(image_path):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()

    stamp_text = f"CERTIFIED BY EAZY CERT\n{datetime.datetime.now().strftime('%Y-%m-%d')}"
    x, y = 50, 50
    text_color = "red"
    border_color = "black"

    text_size = draw.multiline_textsize(stamp_text, font=font)
    padding = 10
    draw.rectangle(
        [x - padding, y - padding, x + text_size[0] + padding, y + text_size[1] + padding],
        outline=border_color,
        width=3
    )
    draw.multiline_text((x, y), stamp_text, fill=text_color, font=font)

    certified_path = image_path.replace(".jpg", "_certified.jpg")
    image.save(certified_path)
    return certified_path