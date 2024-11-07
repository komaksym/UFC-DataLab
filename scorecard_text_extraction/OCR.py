from paddleocr import PaddleOCR
import cv2

def extract_text_from_scorecard(image_path):
    # Initialize PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    
    # Read image
    img = cv2.imread(image_path)
    
    # Perform OCR
    result = ocr.ocr(img)
    
    # Extract text and confidence scores
    extracted_data = []
    for line in result[0]:  # result[0] contains the results
        coordinates = line[0]  # Position of text
        text = line[1][0]     # The actual text
        confidence = line[1][1]  # Confidence score
        
        extracted_data.append({
            'text': text,
            'confidence': confidence,
            'position': coordinates
        })
    
    return extracted_data

# Example usage
image_path = '../datasets/scorecard_images_results/15.jpg'
data = extract_text_from_scorecard(image_path)

# Print results
for item in data:
    if item['confidence'] > 0.7:  # Filter low confidence results
        print(f"Text: {item['text']}, Confidence: {item['confidence']:.2f}")
