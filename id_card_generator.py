
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

def generate_id_card(name, constituency, booth_number, dob, gender,voter_id, photo):
    photo = Image.open(photo)
    id_card = Image.open("voter_idcard_template.jpg")

    # Resize the photo to fit a specific region on the ID card
    photo_width, photo_height = 200, 250  # Define the size of the region for pasting the photo
    photo = photo.resize((photo_width, photo_height))

    # Paste the resized photo onto the ID card template
    id_card.paste(photo, (140, 240))

    # Initialize drawing context
    draw = ImageDraw.Draw(id_card)

    # Load a font
    font_path = "arial.ttf" 
    try:
        font = ImageFont.truetype(font_path, 20)
    except OSError:
    # Fallback to a default font if the specified font is not available
        font = ImageFont.load_default()

    draw.text((320,170), voter_id, fill="black", font=font)

    # Write details on the image
    draw.text((80, 520), f"Name: {name}", fill="black", font=font)
    draw.text((80, 560), f"D.O.B: {dob}", fill="black", font=font)
    draw.text((80, 600), f"Gender: {gender}", fill="black", font=font)
    draw.text((80, 640), f"Voter_Id: {voter_id}", fill="black", font=font)


    return id_card
