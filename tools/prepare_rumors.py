"""
Batch preparation script for:
1. E:\Pokeamice\scan\谎言的真相 2000.5
2. E:\Pokeamice\scan\谎言的真相 2001.4
"""

import os
import hashlib
import json
from PIL import Image

def compute_md5(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def process_batch(source_dir, output_dir, file_specs):
    os.makedirs(os.path.join(output_dir, 'archive'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'web'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'spreads_archive'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'spreads_web'), exist_ok=True)

    manifest = {
        "source_directory": source_dir,
        "destination_directory": output_dir,
        "files": []
    }

    print(f"\n==========================================")
    print(f"Processing: {source_dir} -> {output_dir}")
    print(f"==========================================")

    for spec in file_specs:
        src_file = os.path.join(source_dir, spec['filename'])
        im = Image.open(src_file)
        if im.mode != 'RGB':
            im = im.convert('RGB')
        w, h = im.size

        # 1. Process Spread Archive & Web
        spread_name = spec['spread_name']
        spread_arch_path = os.path.join(output_dir, 'spreads_archive', spread_name)
        im.save(spread_arch_path, 'JPEG', quality=92, subsampling=0)

        # Web spread: height 2048
        scale = 2048.0 / h
        web_w = int(round(w * scale))
        spread_web = im.resize((web_w, 2048), Image.Resampling.LANCZOS)
        spread_web_path = os.path.join(output_dir, 'spreads_web', spread_name)
        spread_web.save(spread_web_path, 'JPEG', quality=84)

        print(f"Saved spread {spread_name}: {w}x{h} -> web {web_w}x2048")

        # 2. Process Single Pages
        if spec.get('is_single', False):
            page_name = spec['page_name']
            arch_p = os.path.join(output_dir, 'archive', page_name)
            im.save(arch_p, 'JPEG', quality=92, subsampling=0)

            scale_p = 2048.0 / h
            pw_web = int(round(w * scale_p))
            page_web = im.resize((pw_web, 2048), Image.Resampling.LANCZOS)
            web_p = os.path.join(output_dir, 'web', page_name)
            page_web.save(web_p, 'JPEG', quality=84)

            manifest['files'].append({
                "page_name": page_name,
                "type": "single_page",
                "width": w,
                "height": h,
                "web_width": pw_web,
                "web_height": 2048,
                "archive_md5": compute_md5(arch_p),
                "web_md5": compute_md5(web_p)
            })
            print(f"  Page {page_name}: {w}x{h} -> web {pw_web}x2048")
        else:
            spine_x = spec['spine_x']
            # Left page: (0, 0, spine_x, h)
            left_im = im.crop((0, 0, spine_x, h))
            left_name = spec['left_name']
            left_arch = os.path.join(output_dir, 'archive', left_name)
            left_im.save(left_arch, 'JPEG', quality=92, subsampling=0)

            scale_l = 2048.0 / h
            lw_web = int(round(left_im.width * scale_l))
            left_web = left_im.resize((lw_web, 2048), Image.Resampling.LANCZOS)
            left_web_path = os.path.join(output_dir, 'web', left_name)
            left_web.save(left_web_path, 'JPEG', quality=84)

            # Right page: (spine_x, 0, w, h)
            right_im = im.crop((spine_x, 0, w, h))
            right_name = spec['right_name']
            right_arch = os.path.join(output_dir, 'archive', right_name)
            right_im.save(right_arch, 'JPEG', quality=92, subsampling=0)

            scale_r = 2048.0 / h
            rw_web = int(round(right_im.width * scale_r))
            right_web = right_im.resize((rw_web, 2048), Image.Resampling.LANCZOS)
            right_web_path = os.path.join(output_dir, 'web', right_name)
            right_web.save(right_web_path, 'JPEG', quality=84)

            # In Japanese books (RTL), right page comes before left page in reading sequence
            for p_name, p_im, p_arch, p_web_path, pw in [
                (right_name, right_im, right_arch, right_web_path, rw_web),
                (left_name, left_im, left_arch, left_web_path, lw_web)
            ]:
                manifest['files'].append({
                    "page_name": p_name,
                    "type": "split_page",
                    "width": p_im.width,
                    "height": p_im.height,
                    "web_width": pw,
                    "web_height": 2048,
                    "archive_md5": compute_md5(p_arch),
                    "web_md5": compute_md5(p_web_path)
                })
                print(f"  Page {p_name}: {p_im.width}x{p_im.height} -> web {pw}x2048")

    manifest_path = os.path.join(output_dir, 'scan-manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Manifest written to {manifest_path}")

# Run Batch 1: 2000.5
batch_2000_5 = [
    {
        "filename": "page001.jpg",
        "spread_name": "spread_cover.jpg",
        "is_single": True,
        "page_name": "p001_cover.jpg"
    },
    {
        "filename": "page002.jpg",
        "spread_name": "spread_p006_p007_toc.jpg",
        "is_single": False,
        "spine_x": 3318,
        "right_name": "p006_toc.jpg",
        "left_name": "p007_toc.jpg"
    },
    {
        "filename": "page003.jpg",
        "spread_name": "spread_p082_p083.jpg",
        "is_single": False,
        "spine_x": 3267,
        "right_name": "p082.jpg",
        "left_name": "p083.jpg"
    },
    {
        "filename": "page004.jpg",
        "spread_name": "spread_p084_p085.jpg",
        "is_single": False,
        "spine_x": 3276,
        "right_name": "p084.jpg",
        "left_name": "p085.jpg"
    }
]

process_batch(
    r"E:\Pokeamice\scan\谎言的真相 2000.5",
    r"E:\Pokeamice\scan\谎言的真相 2000.5_prepared",
    batch_2000_5
)

# Run Batch 2: 2001.4
batch_2001_4 = [
    {
        "filename": "page008.jpg",
        "spread_name": "spread_cover.jpg",
        "is_single": True,
        "page_name": "p001_cover.jpg"
    },
    {
        "filename": "page009.jpg",
        "spread_name": "spread_p078_p079.jpg",
        "is_single": False,
        "spine_x": 3314,
        "right_name": "p078.jpg",
        "left_name": "p079.jpg"
    },
    {
        "filename": "page010.jpg",
        "spread_name": "spread_p080_p081.jpg",
        "is_single": False,
        "spine_x": 3315,
        "right_name": "p080.jpg",
        "left_name": "p081.jpg"
    }
]

process_batch(
    r"E:\Pokeamice\scan\谎言的真相 2001.4",
    r"E:\Pokeamice\scan\谎言的真相 2001.4_prepared",
    batch_2001_4
)
