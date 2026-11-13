"""Turn project GeoTIFFs and U-Net weights into files anyone can open.

GeoTIFF -> PNG picture (any image viewer) + KMZ overlay (Google Earth).
.pth    -> plain-text summary + ONNX file (open at https://netron.app).
"""
import io, os, zipfile
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm, colors


def read_band(path, band=1, scale=1.0, nodata=None, max_side=4000):
    """Read one band, shrunk so the longest side is at most max_side pixels."""
    with rasterio.open(path) as src:
        k = max(1, int(np.ceil(max(src.width, src.height) / max_side)))
        out_shape = (src.height // k, src.width // k)
        a = src.read(band, out_shape=out_shape, resampling=Resampling.average if k > 1 else Resampling.nearest).astype(np.float32)
        raw_nod = src.nodata if nodata is None else nodata
        tr = src.transform * src.transform.scale(src.width / out_shape[1], src.height / out_shape[0])
        crs = src.crs
    mask = np.zeros(a.shape, bool) if raw_nod is None else (a == raw_nod)
    a = a * scale
    a[mask] = np.nan
    return a, tr, crs


def colourise(a, vmin, vmax, cmap="gray", categorical=None):
    """Array -> RGBA uint8, transparent where NaN."""
    if categorical:
        cm_ = colors.ListedColormap(categorical)
        norm = colors.BoundaryNorm(np.arange(len(categorical) + 1) - 0.5, len(categorical))
        rgba = cm_(norm(np.nan_to_num(a, nan=0)))
    else:
        rgba = matplotlib.colormaps[cmap](np.clip((a - vmin) / (vmax - vmin), 0, 1))
    rgba[np.isnan(a), 3] = 0
    return (rgba * 255).astype(np.uint8)


def save_png_with_key(rgba, path, title, key_text, width_in=12.0):
    """Picture with a title strip above and a one-line key below."""
    h, w = rgba.shape[:2]
    img_h = width_in * h / w
    top, bottom = 0.6, 0.5
    H = img_h + top + bottom
    fig = plt.figure(figsize=(width_in, H), dpi=150)
    ax = fig.add_axes([0, bottom / H, 1, img_h / H])
    ax.imshow(rgba, interpolation="nearest"); ax.set_axis_off()
    fig.text(0.01, 1 - 0.3 / H, title, fontsize=13, weight="bold", va="center")
    fig.text(0.01, 0.25 / H, key_text, fontsize=10, va="center")
    fig.savefig(path, facecolor="white"); plt.close(fig)


def save_kmz(rgba, tr, crs, path, name):
    """Reproject an RGBA picture to lat/lon and wrap it as a Google Earth overlay."""
    h, w = rgba.shape[:2]
    left, top = tr * (0, 0); right, bottom = tr * (w, h)
    dst_tr, dw, dh = calculate_default_transform(crs, "EPSG:4326", w, h, left, bottom, right, top)
    out = np.zeros((4, dh, dw), np.uint8)
    for i in range(4):
        reproject(rgba[..., i], out[i], src_transform=tr, src_crs=crs, dst_transform=dst_tr,
                  dst_crs="EPSG:4326", resampling=Resampling.nearest)
    W_, N_ = dst_tr * (0, 0); E_, S_ = dst_tr * (dw, dh)
    buf = io.BytesIO(); Image.fromarray(np.moveaxis(out, 0, -1), "RGBA").save(buf, "PNG")
    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"><GroundOverlay><name>{name}</name>
<Icon><href>overlay.png</href></Icon><LatLonBox><north>{N_}</north><south>{S_}</south>
<east>{E_}</east><west>{W_}</west></LatLonBox></GroundOverlay></kml>"""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("doc.kml", kml); z.writestr("overlay.png", buf.getvalue())


def convert(path, out_dir, name, title, key, band=1, scale=1.0, nodata=None, vmin=0, vmax=1,
            cmap="gray", categorical=None, zero_transparent=False):
    a, tr, crs = read_band(path, band, scale, nodata)
    if zero_transparent:
        a[a == 0] = np.nan
    rgba = colourise(a, vmin, vmax, cmap, categorical)
    save_png_with_key(rgba, f"{out_dir}/{name}.png", title, key)
    save_kmz(rgba, tr, crs, f"{out_dir}/{name}.kmz", title)
    return f"{out_dir}/{name}.png", f"{out_dir}/{name}.kmz"


def summarise_unet(pth_path, out_dir, encoder="resnet34", onnx=True):
    """Readable summary of a U-Net weights file, plus an ONNX copy for netron.app."""
    import torch
    import segmentation_models_pytorch as smp
    name = os.path.splitext(os.path.basename(pth_path))[0]
    model = smp.Unet(encoder, encoder_weights=None, in_channels=2, classes=1)
    sd = torch.load(pth_path, map_location="cpu")
    model.load_state_dict(sd); model.eval()
    lines = [f"U-Net weights file: {os.path.basename(pth_path)}",
             f"Encoder: {encoder} | input: 2 radar layers (VV, VH) | output: 1 water probability per pixel",
             f"Learned numbers: {sum(p.numel() for p in model.parameters()):,}", "",
             "Parameters per part:"]
    for part in ("encoder", "decoder", "segmentation_head"):
        n = sum(p.numel() for k, p in model.named_parameters() if k.startswith(part))
        lines.append(f"  {part:18s} {n:>12,}")
    lines += ["", "Every weight tensor (name, shape, count):"]
    for k, v in sd.items():
        lines.append(f"  {k:60s} {str(tuple(v.shape)):22s} {v.numel():>10,}")
    with open(f"{out_dir}/{name}_summary.txt", "w") as f:
        f.write("\n".join(lines))
    if onnx:
        torch.onnx.export(model, torch.zeros(1, 2, 512, 512), f"{out_dir}/{name}.onnx",
                          input_names=["radar_vv_vh"], output_names=["water_logit"], opset_version=17,
                          dynamic_axes={"radar_vv_vh": {0: "batch", 2: "h", 3: "w"}, "water_logit": {0: "batch", 2: "h", 3: "w"}},
                          dynamo=False)   # one self-contained file, opens in netron.app
    return f"{out_dir}/{name}_summary.txt"
