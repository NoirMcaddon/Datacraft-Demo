# Datacraft CLI Prototype
# © 2025 Mcaddon
# Source-available for education only.
# Redistribution or modification is prohibited.
#आरम्भं कुर्मः

import sys
import os
from math import ceil

try:
    import nbtlib
    from nbtlib.tag import ByteArray, Int, Byte, Compound, String, List
except ImportError:
    print("❌ Bro, install nbtlib first: pip install nbtlib")
    sys.exit(1)

MAP_SIZE = 128 * 128  # Maximum 16384 bytes can be stored in one map
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB max file size (👁️Don't try to change this, buy paid version!i

def bytes_to_colors(data_bytes):
    """Bytes → Minecraft map colors"""
    if len(data_bytes) < MAP_SIZE:
        data_bytes += bytes(MAP_SIZE - len(data_bytes))  # padding

    color_list = []
    for b in data_bytes[:MAP_SIZE]:
        signed_byte = b if b < 128 else b - 256  # convert 0-255 → -128 to 127
        color_list.append(signed_byte)
    return color_list

def colors_to_bytes(color_list):
    """Minecraft colors → original bytes"""
    result = bytearray()
    for c in color_list:
        unsigned = c if c >= 0 else c + 256
        result.append(unsigned)
    return bytes(result)

def create_map_nbt(color_list, map_id):
    """Create a Minecraft map NBT file"""
    data = Compound()
    data["scale"] = Byte(0)
    data["dimension"] = String("minecraft:overworld")
    data["trackingPosition"] = Byte(1)
    data["unlimitedTracking"] = Byte(0)
    data["locked"] = Byte(1)
    data["xCenter"] = Int(map_id * 128)
    data["zCenter"] = Int(map_id * 128)
    data["colors"] = ByteArray(color_list)
    data["banners"] = List[Compound]([])
    data["frames"] = List[Compound]([])
    root = Compound()
    root["data"] = data
    root["DataVersion"] = Int(3465)
    return nbtlib.File(root)

def write_map_file(nbt_file, data_dir, map_id):
    """Save the NBT file"""
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
    """Encode a file into Minecraft maps (5MB limit)"""
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return False
    if not os.path.exists(world_path):
        print(f"❌ World path not found: {world_path}")
        return False

    # Check file size limit
    file_size = os.path.getsize(input_file)
    if file_size > MAX_FILE_SIZE:
        print(f"❌ Your file is TOO BIG! Maximum allowed: {MAX_FILE_SIZE / (1024*1024)} MB")
        print(f"   Your file: {file_size / (1024*1024):.2f} MB")
        print("💡 To store larger files, buy Datacraft Pro from Gumroad!")
        return False

    data_dir = os.path.join(world_path, "data")
    os.makedirs(data_dir, exist_ok=True)

    print(f"\n📂 Reading: {input_file}")
    with open(input_file, "rb") as f:
        file_bytes = f.read()

    num_maps = ceil(file_size / MAP_SIZE)

    print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print(f"🗺️  Maps to create: {num_maps}")
    print(f"🆔 IDs: {start_id} → {start_id + num_maps - 1}\n")

    for i in range(num_maps):
        start = i * MAP_SIZE
        end = min((i + 1) * MAP_SIZE, file_size)
        chunk = file_bytes[start:end]

        colors = bytes_to_colors(chunk)
        map_id = start_id + i
        nbt = create_map_nbt(colors, map_id)
        write_map_file(nbt, data_dir, map_id)

        progress = (i + 1) / num_maps * 100
        print(f"[{progress:5.1f}%] map_{map_id}.dat 🖌️")

    update_idcounts(data_dir, start_id + num_maps - 1)

    print(f"\n✅ Done! {num_maps} maps created 🎉")
    print(f"📋 Try these commands:")
    print(f"   /give @p filled_map[minecraft:map_id={start_id}]")
    if num_maps > 1:
        print(f"   /give @p filled_map[minecraft:map_id={start_id + 1}] ... up to {start_id + num_maps -1}")


    # Save metadata
    meta_file = os.path.join(data_dir, f"mapstore_meta_{start_id}.txt")
    with open(meta_file, "w") as f:
        f.write(f"Filename: {os.path.basename(input_file)}\n")
        f.write(f"OriginalSize: {file_size}\n")
        f.write(f"Maps: {num_maps}\n")
        f.write(f"StartID: {start_id}\n")
        f.write(f"EndID: {start_id + num_maps - 1}\n")
    print(f"💾 Metadata saved: {meta_file}\n")
    return True

def decode_maps(world_path, start_id, num_maps, output_file):
    """Decode Minecraft maps back to the original file"""
    data_dir = os.path.join(world_path, "data")
    if not os.path.exists(data_dir):
        print(f"❌ Data folder not found: {data_dir}")
        return False

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
    output_bytes = bytearray()

    for i in range(num_maps):
        map_id = start_id + i
        map_file = os.path.join(data_dir, f"map_{map_id}.dat")
        if not os.path.exists(map_file):
            print(f"❌ Map missing: map_{map_id}.dat")
            return False

        nbt = nbtlib.load(map_file, gzipped=True)
        colors = nbt.root["data"]["colors"] if hasattr(nbt, 'root') else nbt["data"]["colors"]
        chunk_bytes = colors_to_bytes(colors)
        output_bytes.extend(chunk_bytes)

        progress = (i + 1) / num_maps * 100
        print(f"[{progress:5.1f}%] map_{map_id}.dat 🖌️")

    # Trim padding
    if original_size and original_size < len(output_bytes):
        print(f"\n✂️ Trimming padding: {len(output_bytes):,} → {original_size:,} bytes")
        output_bytes = output_bytes[:original_size]
    else:
        print(f"\n⚠️ No metadata found, padding may remain")

    with open(output_file, "wb") as f:
        f.write(output_bytes)

    print(f"\n✅ Decoded: {output_file} ({len(output_bytes):,} bytes)\n")

    if all(b == 0 for b in output_bytes[:1000]):
        print("⚠️ WARNING: File looks blank/corrupted 😅")
    return True

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("\n🎮 Minecraft Map Storage System\n")
        print("Encode example:")
        print('  python mc_mapstore.py encode file.jpg "C:\\...\\World"\n')
        print("Decode example:")
        print('  python mc_mapstore.py decode "C:\\...\\World" 1000000 207 out.jpg\n')
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



