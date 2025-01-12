import os
import glob
import json
import base64

def process_mes_files_to_base64():
    # Input directory path
    input_dir = '/home/pi/bpq/Mail'
    
    # List to store extracted file data
    processed_files = []
    
    # Get all .mes files in the input directory
    mes_files = glob.glob(os.path.join(input_dir, '*.mes'))
    
    for mes_file in mes_files:
        try:
            with open(mes_file, 'r') as f:
                content = f.read().strip()
                marker_pos = content.find('@!#')
                
                if marker_pos == -1:  # Marker not found
                    continue
                
                # Extract the JSON part (remove the @!# prefix)
                json_str = content[marker_pos+3:]
                
                try:
                    # Parse the JSON data
                    data = json.loads(json_str)
                    
                    # Extract filename and encoded body
                    output_filename = data.get('filename')
                    encoded_body = data.get('body')
                    note = data.get('note')
                    mime_type = data.get('mime_type')
                    
                    if not output_filename or not encoded_body:
                        print(f"Missing required fields in {mes_file}")
                        continue
                    
                    # Decode the base85 content and re-encode in base64
                    try:
                        decoded_content = base64.b85decode(encoded_body)
                        base64_content = base64.b64encode(decoded_content).decode('utf-8')
                        
                        # Append to list
                        processed_files.append({
                            'filename': output_filename,
                            'content_base64': base64_content,
                            'note': note,
                            'mime_type': mime_type
                        })
                        
                        print(f"Successfully processed {mes_file}")
                        
                    except Exception as e:
                        print(f"Error decoding base85 content in {mes_file}: {str(e)}")
                        
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON format in {mes_file}: {str(e)}")
                    
        except Exception as e:
            print(f"Error processing file {mes_file}: {str(e)}")
    
    return processed_files

