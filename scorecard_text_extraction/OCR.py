from PIL import Image

import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/bin/tesseract"

print(pytesseract.image_to_string(Image.open('UFC_AI_Leaderboard/datasets/scorecard_images_results/1.jpg')))
