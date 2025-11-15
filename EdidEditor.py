import argparse
import sys
from pathlib import Path

def read_binary_edid_128(input_file):
    with open(input_file, 'rb') as f:
        edid_data = bytearray(f.read())
    
    if len(edid_data) != 128:
        print(f'WARNING: Not 128 byte length edid: {len(edid_data)} bytes')
    
    return edid_data

def set_manufacturer_serial(edid, serial):
    #0x0C-0x0F -- Manufacturer product serial number
    if len(serial) != 8:
        raise ValueError("Serial must be 8 hex symbols")

    edid[0x0C:0x10] = bytes.fromhex(serial)

    return edid

def set_manufacture_date(edid, week, year):
    #0x10 -- week, 0x11 -- year - 1990
    if not (1 <= week <= 53):
        raise ValueError("Week must be in [1-53]")
    
    if not (1990 <= year <= 2249):
        raise ValueError("Year must be [1990-2249]")
    
    edid[0x10] = week
    edid[0x11] = year - 1990

    return edid

def set_descriptor_text(edid, tag, text):
    #0xFF Descriptor for product serial number, ascii
    #0xFC Descriptor for product name, ascii
    text_bytes = text.encode('ascii', 'ignore')[:13].ljust(13, b' ')
    
    for i in range(4):
        offset = 0x36 + i * 18

        if offset + 18 > len(edid):
            break

        if edid[offset] == 0 and edid[offset+1] == 0 and edid[offset+2] == 0 and edid[offset+3] == tag:
            edid[offset+5:offset+18] = text_bytes

            return edid
        
    raise ValueError(f"Descriptor 0x{tag:02X} not found")

def update_checksum(edid):
    checksum = sum(edid[:127]) % 256
    edid[127] = (0x100 - checksum) % 256

    return edid

def process_edid_file(input_path, output_path, args):
    try:
        edid = read_binary_edid_128(input_path)
        
        if args.serial:
            edid = set_manufacturer_serial(edid, args.serial)
        
        if args.week and args.year:
            edid = set_manufacture_date(edid, args.week, args.year)
        
        if args.product:
            edid = set_descriptor_text(edid, 0xFF, args.product)
        
        edid = update_checksum(edid)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(edid)
    
    except Exception as e:
        print(f"Exception {input_path}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Edit EDID')
    parser.add_argument('input_path', help='Input EDID binary')
    parser.add_argument('output_path', help='Output EDID binary')
    parser.add_argument('--serial', help='Manufacture Serial (8 HEX symbols)')
    parser.add_argument('--week', type=int, help='Produce Week (1-53)')
    parser.add_argument('--year', type=int, help='Produce Year (1990-2249)')
    parser.add_argument('--product', help='Product Serial Number (max 13 symbols)')
    
    args = parser.parse_args()
    
    try:
        input_path = Path(args.input_path)
        output_path = Path(args.output_path)
        
        process_edid_file(input_path, output_path, args)
        
        print(f"\n{input_path} -> {output_path}")
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()