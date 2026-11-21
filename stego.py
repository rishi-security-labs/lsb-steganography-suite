import os
import sys
import zlib
import struct
import hashlib
import secrets
from pathlib import Path
from PIL import Image

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO = True
except ImportError:
    CRYPTO = False

# ── ANSI COLORS ───────────────────────────────────────────────────────────────
R  = "\033[0m"
K  = "\033[30m"
RE = "\033[31m"
GR = "\033[32m"
YE = "\033[33m"
BL = "\033[34m"
MA = "\033[35m"
CY = "\033[36m"
WH = "\033[37m"
BRE = "\033[91m"
BGR = "\033[92m"
BYE = "\033[93m"
BBL = "\033[94m"
BMA = "\033[95m"
BCY = "\033[96m"
BWH = "\033[97m"
BOLD = "\033[1m"
DIM  = "\033[2m"
UL   = "\033[4m"

def c(color, text): return f"{color}{text}{R}"
def bold(text):     return f"{BOLD}{text}{R}"
def dim(text):      return f"{DIM}{text}{R}"

# ── BANNER ────────────────────────────────────────────────────────────────────
BANNER = f"""
{BMA}╔{'═'*54}╗{R}
{BMA}║{R}  {BCY}██████╗{R} {BMA}╔══╗{R}  {BGR}███████╗████████╗███████╗ ██████╗{R}  {BMA}║{R}
{BMA}║{R}  {BCY}██╔════╝{R}{BMA}║  ║{R}  {BGR}██╔════╝╚══██╔══╝██╔════╝██╔════╝{R} {BMA}║{R}
{BMA}║{R}  {BCY}╚█████╗ {R}{BMA}╠══╣{R}  {BGR}███████╗   ██║   █████╗  ██║  ███╗{R} {BMA}║{R}
{BMA}║{R}  {BCY} ╚═══██╗{R}{BMA}║  ║{R}  {BGR}╚════██║   ██║   ██╔══╝  ██║   ██║{R} {BMA}║{R}
{BMA}║{R}  {BCY}██████╔╝{R}{BMA}╚══╝{R}  {BGR}███████║   ██║   ███████╗╚██████╔╝{R} {BMA}║{R}
{BMA}║{R}  {BCY}╚═════╝ {R}      {BGR}╚══════╝   ╚═╝   ╚══════╝ ╚═════╝{R}  {BMA}║{R}
{BMA}║{R}            {BYE}◈  LSB Steganography Suite v3.0  ◈{R}          {BMA}║{R}
{BMA}║{R}        {DIM}encode · decode · encrypt · analyze{R}            {BMA}║{R}
{BMA}╚{'═'*54}╝{R}
"""

# ── UTILS ─────────────────────────────────────────────────────────────────────
def clear(): os.system('clear' if os.name != 'nt' else 'cls')

def header(title):
    clear()
    print(BANNER)
    print(f"  {BMA}╔{'═'*40}╗{R}")
    print(f"  {BMA}║{R}  {bold(BCY + title + R):<50}{BMA}║{R}")
    print(f"  {BMA}╚{'═'*40}╝{R}\n")

def ok(msg):   print(f"  {BGR}[✓]{R} {msg}")
def err(msg):  print(f"  {BRE}[✗]{R} {msg}")
def info(msg): print(f"  {BCY}[i]{R} {msg}")
def warn(msg): print(f"  {BYE}[!]{R} {msg}")
def ask(msg):  return input(f"  {BMA}[?]{R} {msg}").strip()

def pause(): input(f"\n  {DIM}press enter to go back...{R}")

def get_downloads_dir():
    for p in [
        Path('/storage/emulated/0/Download'),
        Path('/sdcard/Download'),
        Path.home() / 'Download',
        Path.home() / 'Downloads',
    ]:
        if p.exists() and os.access(p, os.W_OK):
            return p
    return Path.home()

def progress_bar(done, total, width=30):
    pct = done / total if total else 1
    filled = int(width * pct)
    bar = BGR + '█' * filled + R + DIM + '░' * (width - filled) + R
    print(f"\r  [{bar}] {BCY}{pct*100:.1f}%{R}", end='', flush=True)

# ── BIT I/O ───────────────────────────────────────────────────────────────────
def to_bits(data: bytes):
    for byte in data:
        for i in range(8):
            yield (byte >> i) & 1

def from_bits(bits) -> bytes:
    out = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = sum(bits[i+j] << j for j in range(8))
        out.append(byte)
    return bytes(out)

# ── CAPACITY ──────────────────────────────────────────────────────────────────
def capacity(img: Image.Image, bits_per_channel=1) -> int:
    w, h = img.size
    channels = len(img.getbands())
    return (w * h * channels * bits_per_channel) // 8

# ── ENCODE ────────────────────────────────────────────────────────────────────
MAGIC = b'\xDE\xAD\xBE\xEF'

def build_payload(data: bytes, compress: bool, password: str | None) -> bytes:
    flags = 0
    if compress:
        data = zlib.compress(data, level=9)
        flags |= 0x01
    if password and CRYPTO:
        key = hashlib.sha256(password.encode()).digest()
        nonce = secrets.token_bytes(12)
        data = nonce + AESGCM(key).encrypt(nonce, data, None)
        flags |= 0x02
    checksum = hashlib.md5(data).digest()[:4]
    # MAGIC(4) + flags(1) + length(4) + checksum(4) + data
    return MAGIC + bytes([flags]) + struct.pack('>I', len(data)) + checksum + data

def embed(img: Image.Image, payload: bytes, bits: int = 1) -> Image.Image:
    rgb = img.convert('RGB')
    pixels = list(rgb.getdata())
    bit_stream = list(to_bits(payload))
    total = len(bit_stream)

    if total > len(pixels) * 3 * bits:
        raise ValueError("payload too large for image")

    mask = (1 << bits) - 1
    new_pixels = []
    idx = 0
    for px_i, (r, g, b) in enumerate(pixels):
        for ci, val in enumerate([r, g, b]):
            if idx < total:
                chunk = 0
                for b_i in range(bits):
                    if idx < total:
                        chunk |= bit_stream[idx] << b_i
                        idx += 1
                val = (val & ~mask) | chunk
            [r, g, b][ci] = val if ci > 0 else val
            if ci == 0: r = val
            elif ci == 1: g = val
            else: b = val
        new_pixels.append((r, g, b))
        if px_i % 50000 == 0:
            progress_bar(idx, total)

    progress_bar(total, total)
    print()
    out = Image.new('RGB', rgb.size)
    out.putdata(new_pixels)
    return out

# ── DECODE ────────────────────────────────────────────────────────────────────
def extract(img: Image.Image, bits: int = 1) -> bytes:
    rgb = img.convert('RGB')
    pixels = list(rgb.getdata())
    mask = (1 << bits) - 1
    all_bits = []
    for r, g, b in pixels:
        for val in [r, g, b]:
            for b_i in range(bits):
                all_bits.append((val >> b_i) & 1)

    raw = from_bits(all_bits)

    if raw[:4] != MAGIC:
        raise ValueError("no valid payload found (wrong image or wrong bits/channel)")

    flags = raw[4]
    length = struct.unpack('>I', raw[5:9])[0]
    checksum = raw[9:13]
    data = raw[13:13 + length]

    if hashlib.md5(data).digest()[:4] != checksum:
        raise ValueError("checksum mismatch — data corrupted or tampered")

    return data, flags

def decode_payload(data: bytes, flags: int, password: str | None) -> bytes:
    if flags & 0x02:
        if not CRYPTO:
            raise RuntimeError("cryptography package missing")
        if not password:
            raise ValueError("password required to decrypt")
        key = hashlib.sha256(password.encode()).digest()
        nonce, ct = data[:12], data[12:]
        data = AESGCM(key).decrypt(nonce, ct, None)
    if flags & 0x01:
        data = zlib.decompress(data)
    return data

# ── MENU 1: HIDE TEXT ─────────────────────────────────────────────────────────
def menu_hide_text():
    header("HIDE TEXT IN IMAGE")
    img_path = ask("Image path: ")
    if not img_path or not os.path.isfile(img_path):
        err("file not found"); pause(); return

    try:
        img = Image.open(img_path)
        ok(f"loaded {img.size[0]}x{img.size[1]} {img.mode}")
        cap = capacity(img)
        info(f"capacity: ~{cap} bytes ({cap//1024} KB)\n")
    except Exception as e:
        err(str(e)); pause(); return

    text = ask("text to hide: ")
    if not text: err("empty"); pause(); return

    compress = ask("compress? [Y/n]: ").lower() != 'n'
    encrypt  = ask("encrypt with password? [y/N]: ").lower() == 'y'
    password = ask("password: ") if encrypt else None
    bits_ch  = ask("bits per channel [1/2/4] (1=invisible): ") or "1"
    try: bits_ch = int(bits_ch)
    except: bits_ch = 1
    if bits_ch not in [1, 2, 4]: bits_ch = 1

    out_name = ask("output filename [output.png]: ") or "output.png"
    if not out_name.endswith('.png'): out_name += '.png'

    try:
        payload = build_payload(text.encode('utf-8'), compress, password)
        info(f"payload size: {len(payload)} bytes")
        print(f"  {BYE}embedding...{R}")
        out_img = embed(img, payload, bits_ch)
        dest = get_downloads_dir() / out_name
        out_img.save(dest, 'PNG')
        ok(f"saved → {dest}")
        ok(f"hidden {len(text.encode())} bytes of text")
        if encrypt: ok("AES-256-GCM encrypted ✓")
        if compress: ok("zlib compressed ✓")
    except Exception as e:
        err(str(e))
    pause()

# ── MENU 2: HIDE FILE ─────────────────────────────────────────────────────────
def menu_hide_file():
    header("HIDE FILE IN IMAGE")
    img_path = ask("carrier image path: ")
    if not img_path or not os.path.isfile(img_path):
        err("not found"); pause(); return

    try:
        img = Image.open(img_path)
        cap = capacity(img)
        ok(f"loaded {img.size[0]}x{img.size[1]} | capacity {cap} bytes")
    except Exception as e:
        err(str(e)); pause(); return

    file_path = ask("file to hide: ")
    if not file_path or not os.path.isfile(file_path):
        err("not found"); pause(); return

    file_data = Path(file_path).read_bytes()
    fname = Path(file_path).name.encode('utf-8')
    # prepend filename length + filename + file data
    blob = struct.pack('>H', len(fname)) + fname + file_data
    info(f"file size: {len(file_data)} bytes")

    if len(blob) > cap - 20:
        err(f"file too large. max ~{cap - 20} bytes"); pause(); return

    compress = ask("compress? [Y/n]: ").lower() != 'n'
    encrypt  = ask("encrypt? [y/N]: ").lower() == 'y'
    password = ask("password: ") if encrypt else None
    bits_ch  = int(ask("bits per channel [1/2/4]: ") or "1")
    if bits_ch not in [1,2,4]: bits_ch = 1
    out_name = ask("output filename [carrier.png]: ") or "carrier.png"
    if not out_name.endswith('.png'): out_name += '.png'

    try:
        payload = build_payload(blob, compress, password)
        print(f"  {BYE}embedding...{R}")
        out_img = embed(img, payload, bits_ch)
        dest = get_downloads_dir() / out_name
        out_img.save(dest, 'PNG')
        ok(f"saved → {dest}")
        ok(f"file '{Path(file_path).name}' hidden inside image")
    except Exception as e:
        err(str(e))
    pause()

# ── MENU 3: DECODE ────────────────────────────────────────────────────────────
def menu_decode():
    header("DECODE FROM IMAGE")
    img_path = ask("stego image path: ")
    if not img_path or not os.path.isfile(img_path):
        err("not found"); pause(); return

    bits_ch = int(ask("bits per channel used [1/2/4]: ") or "1")
    if bits_ch not in [1,2,4]: bits_ch = 1
    password = ask("password (leave blank if none): ") or None

    try:
        img = Image.open(img_path)
        print(f"  {BYE}extracting...{R}")
        data, flags = extract(img, bits_ch)
        data = decode_payload(data, flags, password)
    except Exception as e:
        err(str(e)); pause(); return

    # check if file blob or plain text
    try:
        if len(data) > 2:
            fn_len = struct.unpack('>H', data[:2])[0]
            if 1 <= fn_len <= 255:
                fname = data[2:2+fn_len].decode('utf-8')
                if '.' in fname:
                    file_data = data[2+fn_len:]
                    dest = get_downloads_dir() / fname
                    dest.write_bytes(file_data)
                    ok(f"file extracted → {dest}")
                    ok(f"size: {len(file_data)} bytes")
                    pause(); return
    except:
        pass

    # plain text
    try:
        text = data.decode('utf-8')
        print(f"\n  {BMA}╔{'═'*44}╗{R}")
        print(f"  {BMA}║{R}  {bold('HIDDEN MESSAGE'):<52}{BMA}║{R}")
        print(f"  {BMA}╠{'═'*44}╣{R}")
        for line in text.split('\n'):
            print(f"  {BMA}║{R}  {BWH}{line:<50}{R}{BMA}║{R}")
        print(f"  {BMA}╚{'═'*44}╝{R}")
        info(f"length: {len(data)} bytes")
    except:
        warn("binary data — saving as 'decoded.bin'")
        dest = get_downloads_dir() / 'decoded.bin'
        dest.write_bytes(data)
        ok(f"saved → {dest}")
    pause()

# ── MENU 4: ANALYZE ───────────────────────────────────────────────────────────
def menu_analyze():
    header("ANALYZE IMAGE")
    img_path = ask("image path: ")
    if not img_path or not os.path.isfile(img_path):
        err("not found"); pause(); return

    try:
        img = Image.open(img_path)
        rgb = img.convert('RGB')
        pixels = list(rgb.getdata())
        w, h = img.size
    except Exception as e:
        err(str(e)); pause(); return

    print(f"\n  {BMA}╔{'═'*44}╗{R}")
    print(f"  {BMA}║{R}  {bold(BCY+'IMAGE STATS'+R):<52}{BMA}║{R}")
    print(f"  {BMA}╠{'═'*44}╣{R}")

    rows = [
        ("Dimensions",  f"{w} x {h} px"),
        ("Mode",        img.mode),
        ("Total pixels",f"{w*h:,}"),
        ("Cap @ 1bit",  f"{capacity(img,1):,} bytes ({capacity(img,1)//1024} KB)"),
        ("Cap @ 2bit",  f"{capacity(img,2):,} bytes ({capacity(img,2)//1024} KB)"),
        ("Cap @ 4bit",  f"{capacity(img,4):,} bytes ({capacity(img,4)//1024} KB)"),
    ]

    for k_, v_ in rows:
        print(f"  {BMA}║{R}  {BYE}{k_:<18}{R}{BWH}{v_:<28}{R}{BMA}║{R}")

    # LSB distribution (chi-square hint)
    lsb_ones = sum((r & 1) + (g & 1) + (b & 1) for r,g,b in pixels)
    total_bits = len(pixels) * 3
    lsb_ratio = lsb_ones / total_bits
    natural = abs(lsb_ratio - 0.5) < 0.03
    stego_hint = f"{BRE}POSSIBLE STEGO{R}" if not natural else f"{BGR}LOOKS CLEAN{R}"

    print(f"  {BMA}╠{'═'*44}╣{R}")
    print(f"  {BMA}║{R}  {BYE}{'LSB ratio':<18}{R}{lsb_ratio:.4f} → {stego_hint:<30}{BMA}║{R}")
    print(f"  {BMA}╚{'═'*44}╝{R}")

    # check for magic header
    print(f"\n  {BYE}checking for stego signature...{R}")
    try:
        data, flags = extract(img, 1)
        ok(f"MAGIC FOUND — payload detected ({len(data)} bytes)")
        enc = "yes" if flags & 0x02 else "no"
        cmp = "yes" if flags & 0x01 else "no"
        info(f"encrypted: {enc} | compressed: {cmp}")
    except:
        info("no recognizable payload at 1bpc")

    pause()

# ── MENU 5: CLONE METADATA ────────────────────────────────────────────────────
def menu_clone_meta():
    header("CLONE METADATA")
    info("copies EXIF/metadata from one image to another (cover your tracks)\n")
    src = ask("source image (with real metadata): ")
    dst = ask("target image (stego output): ")

    if not os.path.isfile(src) or not os.path.isfile(dst):
        err("file not found"); pause(); return

    try:
        from PIL import Image as PILImage
        import piexif
        src_img = PILImage.open(src)
        dst_img = PILImage.open(dst)

        try:
            exif = piexif.load(src_img.info.get('exif', b''))
        except:
            exif = {"0th":{}, "Exif":{}, "GPS":{}, "1st":{}}

        exif_bytes = piexif.dump(exif)
        out_path = get_downloads_dir() / ("meta_" + Path(dst).name)
        dst_img.save(out_path, exif=exif_bytes)
        ok(f"metadata cloned → {out_path}")
    except ImportError:
        warn("piexif not installed. run: pip install piexif")
    except Exception as e:
        err(str(e))
    pause()

# ── MENU 6: COMPARE IMAGES ────────────────────────────────────────────────────
def menu_compare():
    header("COMPARE IMAGES (DIFF)")
    img1_p = ask("original image: ")
    img2_p = ask("stego image: ")

    if not os.path.isfile(img1_p) or not os.path.isfile(img2_p):
        err("file(s) not found"); pause(); return

    try:
        i1 = Image.open(img1_p).convert('RGB')
        i2 = Image.open(img2_p).convert('RGB')

        if i1.size != i2.size:
            err("images must be same size"); pause(); return

        p1 = list(i1.getdata())
        p2 = list(i2.getdata())

        diffs = sum(1 for a, b in zip(p1, p2) if a != b)
        total = len(p1)
        pct = diffs / total * 100

        print(f"\n  {BMA}╔{'═'*40}╗{R}")
        print(f"  {BMA}║{R}  {bold(BCY+'DIFF RESULTS'+R):<50}{BMA}║{R}")
        print(f"  {BMA}╠{'═'*40}╣{R}")
        print(f"  {BMA}║{R}  {BYE}{'Changed pixels':<20}{R}{BWH}{diffs:,} / {total:,}{R:<20}{BMA}║{R}")
        print(f"  {BMA}║{R}  {BYE}{'Difference %':<20}{R}{BWH}{pct:.4f}%{R:<26}{BMA}║{R}")
        vis = f"{BGR}invisible{R}" if pct < 0.1 else f"{BYE}slight{R}" if pct < 1 else f"{BRE}visible{R}"
        print(f"  {BMA}║{R}  {BYE}{'Visibility':<20}{R}{vis:<40}{BMA}║{R}")
        print(f"  {BMA}╚{'═'*40}╝{R}")

        # save diff image
        diff_pixels = [
            (255,0,0) if a != b else (0,0,0)
            for a, b in zip(p1, p2)
        ]
        diff_img = Image.new('RGB', i1.size)
        diff_img.putdata(diff_pixels)
        dest = get_downloads_dir() / "diff_map.png"
        diff_img.save(dest)
        ok(f"diff map saved → {dest}")

    except Exception as e:
        err(str(e))
    pause()

# ── MAIN MENU ─────────────────────────────────────────────────────────────────
MENU_ITEMS = [
    (BGR,  "1", "Hide text in image",          menu_hide_text),
    (BCY,  "2", "Hide file in image",           menu_hide_file),
    (BMA,  "3", "Decode / extract",             menu_decode),
    (BYE,  "4", "Analyze image (chi-square)",   menu_analyze),
    (BBL,  "5", "Clone metadata (EXIF spoof)",  menu_clone_meta),
    (BRE,  "6", "Compare images (diff map)",    menu_compare),
    (DIM,  "0", "Exit",                         None),
]

def main():
    while True:
        clear()
        print(BANNER)
        print(f"  {BMA}╔{'═'*42}╗{R}")
        print(f"  {BMA}║{R}  {bold(BYE + '◈  MAIN MENU' + R):<52}{BMA}║{R}")
        print(f"  {BMA}╠{'═'*42}╣{R}")
        for color, num, label, _ in MENU_ITEMS:
            num_fmt  = f"{color}[{num}]{R}"
            lbl_fmt  = f"{BWH}{label}{R}"
            print(f"  {BMA}║{R}    {num_fmt}  {lbl_fmt:<45}{BMA}║{R}")
        print(f"  {BMA}╚{'═'*42}╝{R}")

        if not CRYPTO:
            warn(f"{DIM}cryptography pkg missing — encryption disabled. pip install cryptography{R}")

        choice = ask("\n  select > ")
        for color, num, label, fn in MENU_ITEMS:
            if choice == num:
                if fn:
                    fn()
                else:
                    clear()
                    print(f"\n  {DIM}bye.{R}\n")
                    sys.exit(0)
                break
        else:
            warn("invalid"); input()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {DIM}interrupted.{R}\n")
        sys.exit(0)
