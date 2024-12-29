
import pytesseract
from PIL import Image
import json
import re

# Specifying the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'  # Replace with your actual Tesseract path

def convert_data(data):
    """
    Converts the provided JSON data to the desired format.

    Args:
        data: The original JSON data.

    Returns:
        A list of dictionaries representing the extracted table rows.
    """

    if not data:  # Check if data is empty
        return []  # Return an empty list if so

    converted_data = []
    for row in data["data"]:
        new_row = {}
        if "CW" in row:
            new_row["rack_no"] = row["CW"]  # Assuming "CW" represents rack_no
        if "I" in row:
            new_row["id"] = row["I"]  # Assuming "I" represents ID (top part)
        if "ee" in row:
            try:
                new_row["insp_no"] = int(row["ee"].split()[0])
            except (ValueError, IndexError):  # Handle potential errors (ValueError and IndexError)
                new_row["insp_no"] = None  # Set to None if conversion fails
        if "nS" in row:
            if "id" in new_row and row["nS"]:  # Assuming "nS" represents ID (bottom part)
                new_row["id"] = {"top": new_row["id"], "bottom": row["nS"]}
            elif "defects" not in new_row and row["nS"].strip():  # Assuming "nS" represents defects
                new_row["defects"] = [row["nS"].strip()]
        converted_data.append(new_row)

    return converted_data

def extract_table_data(image_path):
    """
    Extracts handwritten tabular data from the image and converts it to JSON.

    Args:
        image_path: Path to the image file.

    Returns:
        A JSON object representing the extracted data.
    """

    try:
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img)

        # Split the text into lines
        lines = extracted_text.strip().split('\n')

        # Find the header row (assumes first non-empty line is the header)
        header_row = None
        for line in lines:
            if line.strip():
                header_row = line.split()
                break

        # Extract data rows
        data_rows = []
        for line in lines[1:]:
            if line.strip():
                data_row = line.split()
                data_rows.append(data_row)

        # Create a list to store the extracted data in JSON format
        data = []

        # Iterate through the data rows and extract values
        for row in data_rows:
            row_data = {}
            for i, value in enumerate(row):
                if i < len(header_row):
                    field_name = header_row[i].strip()
                    row_data[field_name] = value.strip()

            # Handle special cases and formatting (adjust as needed)
            if "ID" in row_data:
                try:
                    top_id = re.findall(r'\d+', row_data["ID"])[0]
                    bottom_id = re.findall(r'\d+', row_data["ID"])[1]
                    row_data["ID"] = {"top": top_id, "bottom": bottom_id}
                except IndexError:
                    row_data["ID"] = None

            # Add the extracted data to the list
            data.append(row_data)

        # Create the final JSON object
        json_data = {"data": data}

        return json_data

    except Exception as e:
        print(f"Error extracting data: {e}")
        return None

# Example usage
image_path = "1.jpg"  # Replace with the actual image path

# Extract data from the image
extracted_json = extract_table_data(image_path)

if extracted_json:
    # Convert the extracted data
    converted_data = convert_data(extracted_json)

    # Save the converted data to a JSON file
    with open("output.json", "w") as f:
        json.dump(converted_data, f, indent=4)

    print("Data extracted and saved to output.json")
else:
    print("Error extracting data from image.")