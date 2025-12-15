# Datacraft CLI Prototype
# © 2025 Mcaddon
# Source-available for education only.
# Redistribution or modification is prohibited.

import sys
import os
from math import ceil

try:
    import nbtlib
    from nbtlib.tag import ByteArray, Int, Byte, Compound, String, List
except ImportError:
    print("ERROR: pip install nbtlib")
    sys.exit(1)

MAP_SIZE = 128 * 128  # 16384 bytes per map

def bytes_to_colors(data):
    """
    Convert raw bytes to Minecraft color IDs
    Store original byte values directly as signed bytes
    """
    if len(data) < MAP_SIZE:
        data = data + bytes(MAP_SIZE - len(data))
    
    colors = []
    for byte in data[:MAP_SIZE]:
        # Convert to signed byte (-128 to 127)
        signed = byte if byte < 128 else byte - 256
        colors.append(signed)
    
    return colors

def colors_to_bytes(colors):
    """
    Convert Minecraft color IDs back to original bytes
    """
    data = bytearray()
    for color in colors:
        # Convert signed byte back to unsigned (0-255)
        unsigned = color if color >= 0 else color + 256
        data.append(unsigned)
    return bytes(data)

def create_map_nbt(color_data, map_id):
    """
    Create visible Minecraft map
    """
    data = Compound()
    data["scale"] = Byte(0)
    data["dimension"] = String("minecraft:overworld")
    data["trackingPosition"] = Byte(1)
    data["unlimitedTracking"] = Byte(0)
    data["locked"] = Byte(1)
    data["xCenter"] = Int(map_id * 128)
    data["zCenter"] = Int(map_id * 128)
    data["colors"] = ByteArray(color_data)
    data["banners"] = List[Compound]([])
    data["frames"] = List[Compound]([])
    
    root = Compound()
    root["data"] = data
    root["DataVersion"] = Int(3465)
    
    return nbtlib.File(root)

def write_map_file(nbt_file, data_dir, map_id):
    """Write map file"""
    filepath = os.path.join(data_dir, f"map_{map_id}.dat")
    nbt_file.save(filepath, gzipped=True)
    return filepath

def update_idcounts(data_dir, highest_id):
    """Update idcounts.dat"""
    path = os.path.join(data_dir, "idcounts.dat")
    root = Compound()
    data = Compound()
    data["map"] = Int(highest_id)
    root["data"] = data
    root["DataVersion"] = Int(3465)
    nbtlib.File(root).save(path, gzipped=True)

def encode_file(input_file, world_path, start_id=1000000):
    """Encode file to maps"""
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return False
    
    if not os.path.exists(world_path):
        print(f"❌ World not found: {world_path}")
        return False
    
    data_dir = os.path.join(world_path, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"\n📂 Reading: {input_file}")
    with open(input_file, "rb") as f:
        file_data = f.read()
    
    file_size = len(file_data)
    num_maps = ceil(file_size / MAP_SIZE)
    
    print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print(f"🗺️  Maps: {num_maps}")
    print(f"🆔 Range: {start_id} to {start_id + num_maps - 1}\n")
    
    # Create maps
    for i in range(num_maps):
        start_byte = i * MAP_SIZE
        end_byte = min((i + 1) * MAP_SIZE, file_size)
        chunk = file_data[start_byte:end_byte]
        
        color_data = bytes_to_colors(chunk)
        map_id = start_id + i
        nbt_file = create_map_nbt(color_data, map_id)
        write_map_file(nbt_file, data_dir, map_id)
        
        progress = (i + 1) / num_maps * 100
        print(f"[{progress:5.1f}%] map_{map_id}.dat")
    
    update_idcounts(data_dir, start_id + num_maps - 1)
    
    print(f"\n✅ SUCCESS! {num_maps} maps created\n")
    print(f"📋 Minecraft commands:")
    print(f"   /give @p filled_map{{map:{start_id}}}")
    if num_maps > 1:
        print(f"   /give @p filled_map{{map:{start_id + 1}}}")
        print(f"   ... (up to {start_id + num_maps - 1})\n")
    
    # Save metadata with exact file size
    meta_file = os.path.join(data_dir, f"mapstore_meta_{start_id}.txt")
    with open(meta_file, "w") as f:
        f.write(f"Filename: {os.path.basename(input_file)}\n")
        f.write(f"OriginalSize: {file_size}\n")
        f.write(f"Maps: {num_maps}\n")
        f.write(f"StartID: {start_id}\n")
        f.write(f"EndID: {start_id + num_maps - 1}\n")
    
    print(f"💾 Metadata: {meta_file}\n")
    
    return True

def decode_maps(world_path, start_id, num_maps, output_file):
    """Decode maps to original file"""
    data_dir = os.path.join(world_path, "data")
    
    if not os.path.exists(data_dir):
        print(f"❌ Data folder not found: {data_dir}")
        return False
    
    # Try to read metadata for original size
    meta_file = os.path.join(data_dir, f"mapstore_meta_{start_id}.txt")
    original_size = None
    
    if os.path.exists(meta_file):
        print(f"📄 Reading metadata...")
        with open(meta_file, "r") as f:
            for line in f:
                if "OriginalSize:" in line:
                    original_size = int(line.split(":")[1].strip())
                    print(f"   Original size: {original_size:,} bytes")
                    break
    
    print(f"\n🔍 Decoding {num_maps} maps from ID {start_id}\n")
    
    output_data = bytearray()
    
    # Read all maps
    for i in range(num_maps):
        map_id = start_id + i
        map_file = os.path.join(data_dir, f"map_{map_id}.dat")
        
        if not os.path.exists(map_file):
            print(f"❌ Map not found: map_{map_id}.dat")
            return False
        
        # Load NBT
        nbt_file = nbtlib.load(map_file, gzipped=True)
        
        # Get colors array
        if hasattr(nbt_file, 'root'):
            colors = nbt_file.root["data"]["colors"]
        else:
            colors = nbt_file["data"]["colors"]
        
        # Convert back to bytes
        chunk_bytes = colors_to_bytes(colors)
        output_data.extend(chunk_bytes)
        
        progress = (i + 1) / num_maps * 100
        print(f"[{progress:5.1f}%] map_{map_id}.dat")
    
    # Trim to original size (remove padding)
    if original_size and original_size < len(output_data):
        print(f"\n✂️  Trimming padding: {len(output_data):,} → {original_size:,} bytes")
        output_data = output_data[:original_size]
    else:
        print(f"\n⚠️  Warning: No metadata found - file may have padding")
    
    # Write output
    with open(output_file, "wb") as f:
        f.write(output_data)
    
    print(f"\n✅ Decoded: {output_file}")
    print(f"📊 Size: {len(output_data):,} bytes ({len(output_data)/1024:.2f} KB)\n")
    
    # Verify it's not all zeros
    if all(b == 0 for b in output_data[:1000]):
        print("⚠️  WARNING: File appears to be blank/corrupted!")
        print("   Check if maps were created correctly\n")
    
    return True

def main():
    """CLI"""
    if len(sys.argv) < 2:
        print("\n🎮 Minecraft Map Storage System\n")
        print("Encode:")
        print('  python mc_mapstore.py encode file.jpg "C:\\...\\saves\\World"\n')
        print("Decode:")
        print('  python mc_mapstore.py decode "C:\\...\\saves\\World" 1000000 207 out.jpg\n')
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "encode":
        if len(sys.argv) < 4:
            print("❌ Usage: encode <file> <world_path> [start_id]")
            sys.exit(1)
        
        input_file = sys.argv[2]
        world_path = sys.argv[3]
        start_id = int(sys.argv[4]) if len(sys.argv) > 4 else 1000000
        
        success = encode_file(input_file, world_path, start_id)
        sys.exit(0 if success else 1)
    
    elif cmd == "decode":
        if len(sys.argv) < 6:
            print("❌ Usage: decode <world_path> <start_id> <num_maps> <output>")
            sys.exit(1)
        
        world_path = sys.argv[2]
        start_id = int(sys.argv[3])
        num_maps = int(sys.argv[4])
        output_file = sys.argv[5]
        
        success = decode_maps(world_path, start_id, num_maps, output_file)
        sys.exit(0 if success else 1)
    
    else:
        print(f"❌ Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
