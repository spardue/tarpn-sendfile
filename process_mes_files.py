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
                json_str = content[marker_pos+3:].strip()
                
                try:
                    # Parse the JSON data
                    data = json.loads(json_str)
                    print(mes_file, data)
                    
                    # Extract filename and encoded body
                    output_filename = data.get('filename')
                    encoded_body = data.get('body')
                    note = data.get('note')
                    mimetype = data.get('mimetype')
                    to = data.get('to')
                    _from = data.get('from')
                    
                    have_all_fields = output_filename and encoded_body and mimetype and to and _from
                    if not have_all_fields:
                        print(f"Missing required fields in {mes_file}")
                        continue
                    
                    # Decode the base85 content and re-encode in base64
                    try:
                        decoded_content = base64.b85decode(encoded_body)
                        base64_content = base64.b64encode(decoded_content).decode('utf-8')
                        
                        # Append to list
                        processed_files.append({
                            'filename': output_filename,
                            'body': base64_content,
                            'note': note,
                            'mimetype': mimetype,
                            'to': to,
                            'from': _from

                        })
                        
                        print(f"Successfully processed {mes_file}")
                        
                    except Exception as e:
                        print(f"Error decoding base85 content in {mes_file}: {str(e)}")
                        
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON format in {mes_file}: {str(e)}", json_str)
                    
        except Exception as e:
            print(f"Error processing file {mes_file}: {str(e)}")
    
    return processed_files

