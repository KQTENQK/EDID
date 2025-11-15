import os
import sys
from pathlib import Path

#EDID 1.4
def get_resolution(edid_bytes):
    try:
        if edid_bytes[0:8] != [0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00]:
            return "invalid_header"
        
        for i in range(4):
            offset = 0x36 + i * 18

            if offset + 18 > len(edid_bytes):
                break
            
            if edid_bytes[offset] == 0 and edid_bytes[offset+1] == 0:
                continue
            
            if (edid_bytes[offset+17] & 0x80) == 0x80:
                continue
            
            h_active = edid_bytes[offset+2] | ((edid_bytes[offset+4] & 0xF0) << 4)
            v_active = edid_bytes[offset+5] | ((edid_bytes[offset+7] & 0xF0) << 4)
            
            if h_active == 0 or v_active == 0:
                continue
                
            return f"{h_active}x{v_active}"
        
        for i in range(0, 24, 2):
            std_timing = edid_bytes[0x26 + i]

            if std_timing == 0x01:
                continue
                
            h_res = (std_timing >> 2) * 8 + 248
            v_ratio = (std_timing & 0x03)
            v_res = h_res * {0: 16/16, 1: 10/16, 2: 4/5, 3: 9/16}[v_ratio]

            return f"{h_res}x{int(v_res)}"
        
        h_active = (edid_bytes[0x38] << 8) | edid_bytes[0x39]
        v_active = (edid_bytes[0x3B] << 8) | edid_bytes[0x3A]

        return f"{h_active}x{v_active}"
    
    except Exception as e:
        print(f"Resolution detection error: {str(e)}")
        return "unknown"

def process_edid_file(input_path, relative_path, output_base):
    try:
        bytes_list = []

        with open(input_path, 'r') as f:
            for line in f:
                if line.startswith('edid'):
                    continue

                clean_line = line.strip()
                
                if clean_line.startswith('---'):
                    break
                
                if not clean_line:
                    continue
                
                parts = [p for p in line.split() 
                        if len(p) == 2 and p != '--' ]
                
                if not parts:
                    continue
                
                try:
                    bytes_list.extend([int(b, 16) for b in parts])
                except ValueError:
                    continue

        if len(bytes_list) not in [128, 256, 384, 512, 640, 768, 1024]:
            raise ValueError(f"Incorrect EDID size: {len(bytes_list)} bytes")

        resolution = get_resolution(bytes_list)
        
        #relative_path = input_path.relative_to(input_path)
        output_path = output_base / resolution / relative_path.with_suffix('.bin')

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(bytes(bytes_list))
            
        print(f"Processed: {input_path.name} -> {output_path.name}")

    except Exception as e:
        print(f"Exception {relative_path.name}: {str(e)}")

def process_directory(input_dir, output_dir):
    input_dir = Path(input_dir).resolve()
    output_dir = Path(output_dir).resolve()
    
    if not input_dir.exists():
        raise FileNotFoundError(f"Not found: {input_dir}")
    
    for input_file in input_dir.rglob('*'):
        if input_file.is_file():
            relative_path = input_file.relative_to(input_dir)
            #output_file = output_dir / relative_path.with_suffix('.bin')
            
            process_edid_file(input_file, relative_path, output_dir)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python ToHex.py <input_directory> <output_directory>")
        sys.exit(1)
        
    try:
        process_directory(sys.argv[1], sys.argv[2])
        print("\nSuccess!")
    except Exception as e:
        print(f"Exception: {str(e)}")
        sys.exit(1)