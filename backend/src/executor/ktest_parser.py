import struct
import os

def parse_ktest(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Ktest file not found: {path}")

    with open(path, "rb") as f:
        data = f.read()

    ptr = 0
    
    # 1. Check Magic Header ('KTEST')
    if len(data) < 5 or data[ptr:ptr+5] != b'KTEST':
        return {"valid": False, "error": "Invalid file format"}
    ptr += 5

    # 2. Read Version (4 bytes)
    version = struct.unpack(">I", data[ptr:ptr+4])[0]
    ptr += 4

    # 3. Read Args (4 bytes num + strings)
    num_args = struct.unpack(">I", data[ptr:ptr+4])[0]
    ptr += 4
    
    args = []
    for _ in range(num_args):
        size = struct.unpack(">I", data[ptr:ptr+4])[0]
        ptr += 4
        arg = data[ptr:ptr+size].decode('utf-8', errors='ignore')
        ptr += size
        args.append(arg)

    # --- FIX START: Skip Symbolic Args (Hidden in V3) ---
    if version >= 2:
        # These 8 bytes + data were trapping us!
        sym_argvs = struct.unpack(">I", data[ptr:ptr+4])[0]
        ptr += 4
        sym_argv_len = struct.unpack(">I", data[ptr:ptr+4])[0]
        ptr += 4
        ptr += sym_argv_len # Skip the actual symbolic arg data
    # --- FIX END ---

    # 4. Read Objects (Now we are at the right address!)
    num_objects = struct.unpack(">I", data[ptr:ptr+4])[0]
    ptr += 4

    objects = []
    for _ in range(num_objects):
        name_size = struct.unpack(">I", data[ptr:ptr+4])[0]
        ptr += 4
        
        name = data[ptr:ptr+name_size].decode('utf-8', errors='ignore')
        ptr += name_size
        
        data_size = struct.unpack(">I", data[ptr:ptr+4])[0]
        ptr += 4
        
        obj_bytes = data[ptr:ptr+data_size]
        ptr += data_size
        
        # Convert bytes based on size and KLEE's little-endian convention
        int_val = None
        if data_size in [1, 2, 4, 8]:
             int_val = int.from_bytes(obj_bytes, byteorder='little', signed=True)
        else:
             int_val = "Non-standard size: " + str(data_size)

        objects.append({
            "name": name,
            "size": data_size,
            "int_value": int_val,
            "raw_bytes": list(obj_bytes)
        })

    return {
        "valid": True,
        "version": version,
        "args": args,
        "objects": objects
    }

def parse_klee_error(path: str):
    """
    Parses a KLEE .err file to extract bug details.
    Ref: SRS FR6 (Fault Detection)
    """
    if not os.path.exists(path):
        return {"error": "Error file not found"}

    details = {
        "type": "Unknown",
        "file": "Unknown",
        "line": 0,
        "message": "",
        "assembly_line": 0
    }

    try:
        with open(path, "r") as f:
            lines = f.readlines()
            
            # Line 1: Error: <Type>
            if len(lines) > 0:
                details["message"] = lines[0].strip()
                if "Error: " in lines[0]:
                    details["type"] = lines[0].split("Error: ")[1].strip()
            
            # Line 2: File: <Name>
            if len(lines) > 1 and "File: " in lines[1]:
                details["file"] = lines[1].split("File: ")[1].strip()

            # Line 3: Line: <Number>
            if len(lines) > 2 and "Line: " in lines[2]:
                try:
                    details["line"] = int(lines[2].split("Line: ")[1].strip())
                except ValueError:
                    pass
            
            # Line 4: assembly.ll line ...
            if len(lines) > 3 and "assembly.ll " in lines[3]:
                 try:
                    details["assembly_line"] = int(lines[3].split("line ")[1].strip())
                 except ValueError:
                    pass

    except Exception as e:
        details["parse_error"] = str(e)

    return details