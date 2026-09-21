#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EDA de INDIGO Crack Detection.

Lee únicamente:
  data/raw/indigo/train/train_100/
  data/raw/indigo/test/test_100/

Ignora __MACOSX, ._* , .DS_Store y ZIP.
No convierte VOC a YOLO. No entrena. No modifica imágenes ni XML.
"""

from __future__ import annotations

import argparse
import json
import random
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parents[1]
INDIGO = REPO_ROOT / "data" / "raw" / "indigo"
SPLITS = {
    "train": INDIGO / "train" / "train_100",
    "test": INDIGO / "test" / "test_100",
}
OUT_DIR = REPO_ROOT / "evaluation" / "eda"
SEED = 42

# Umbrales de calidad (relativos al área de la imagen).
AREA_REL_MUY_PEQ = 0.001
AREA_REL_MUY_GRANDE = 0.80


def configurar_salida() -> None:
    import sys

    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def es_auxiliar(ruta: Path) -> bool:
    nombre = ruta.name
    if nombre.startswith("._") or nombre in {".DS_Store", "_extracted.ok"}:
        return True
    return "__MACOSX" in ruta.parts


def parsear_xml(xml_path: Path) -> dict | None:
    try:
        raiz = ET.parse(xml_path).getroot()
    except ET.ParseError:
        return None
    w = int(float(raiz.findtext("size/width") or 0))
    h = int(float(raiz.findtext("size/height") or 0))
    objetos = []
    for obj in raiz.findall("object"):
        bb = obj.find("bndbox")
        if bb is None:
            continue
        xmin = float(bb.findtext("xmin") or 0)
        ymin = float(bb.findtext("ymin") or 0)
        xmax = float(bb.findtext("xmax") or 0)
        ymax = float(bb.findtext("ymax") or 0)
        objetos.append(
            {
                "clase": (obj.findtext("name") or "").strip(),
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax,
            }
        )
    return {
        "xml": xml_path,
        "filename": raiz.findtext("filename") or xml_path.with_suffix(".jpg").name,
        "width": w,
        "height": h,
        "objetos": objetos,
    }


def cargar() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    filas_img = []
    filas_box = []
    xml_invalidos = []
    jpg_sin_xml = []
    xml_sin_jpg = []

    for split, carpeta in SPLITS.items():
        jpgs = sorted(
            p for p in carpeta.glob("*.jpg") if p.is_file() and not es_auxiliar(p)
        )
        xmls = sorted(
            p for p in carpeta.glob("*.xml") if p.is_file() and not es_auxiliar(p)
        )
        stems_jpg = {p.stem: p for p in jpgs}
        stems_xml = {p.stem: p for p in xmls}
        for stem, jpg in stems_jpg.items():
            if stem not in stems_xml:
                jpg_sin_xml.append(str(jpg.relative_to(REPO_ROOT)))
        for stem, xml in stems_xml.items():
            if stem not in stems_jpg:
                xml_sin_jpg.append(str(xml.relative_to(REPO_ROOT)))
            parsed = parsear_xml(xml)
            if parsed is None:
                xml_invalidos.append(str(xml.relative_to(REPO_ROOT)))
                continue
            jpg = stems_jpg.get(stem)
            clases = [o["clase"] for o in parsed["objetos"]]
            filas_img.append(
                {
                    "split": split,
                    "stem": stem,
                    "jpg": str(jpg) if jpg else None,
                    "xml": str(xml),
                    "width": parsed["width"],
                    "height": parsed["height"],
                    "n_objetos": len(parsed["objetos"]),
                    "tiene_egg": "egg" in clases,
                    "tiene_crack": "crack" in clases,
                    "n_egg": sum(c == "egg" for c in clases),
                    "n_crack": sum(c == "crack" for c in clases),
                }
            )
            for obj in parsed["objetos"]:
                bw = obj["xmax"] - obj["xmin"]
                bh = obj["ymax"] - obj["ymin"]
                area = bw * bh
                img_area = parsed["width"] * parsed["height"] if parsed["width"] and parsed["height"] else np.nan
                cx = (obj["xmin"] + obj["xmax"]) / 2
                cy = (obj["ymin"] + obj["ymax"]) / 2
                filas_box.append(
                    {
                        "split": split,
                        "stem": stem,
                        "clase": obj["clase"],
                        "xmin": obj["xmin"],
                        "ymin": obj["ymin"],
                        "xmax": obj["xmax"],
                        "ymax": obj["ymax"],
                        "bbox_w": bw,
                        "bbox_h": bh,
                        "area": area,
                        "area_rel": area / img_area if img_area else np.nan,
                        "aspect": bw / bh if bh else np.nan,
                        "cx_rel": cx / parsed["width"] if parsed["width"] else np.nan,
                        "cy_rel": cy / parsed["height"] if parsed["height"] else np.nan,
                        "fuera": (
                            obj["xmin"] < 0
                            or obj["ymin"] < 0
                            or obj["xmax"] > parsed["width"]
                            or obj["ymax"] > parsed["height"]
                        ),
                        "degenerada": bw <= 0 or bh <= 0,
                    }
                )

    imagenes = pd.DataFrame(filas_img)
    cajas = pd.DataFrame(filas_box)
    meta = {
        "xml_invalidos": xml_invalidos,
        "jpg_sin_xml": jpg_sin_xml,
        "xml_sin_jpg": xml_sin_jpg,
    }
    return imagenes, cajas, meta


def iou(a: pd.Series, b: pd.Series) -> float:
    ix1 = max(a.xmin, b.xmin)
    iy1 = max(a.ymin, b.ymin)
    ix2 = min(a.xmax, b.xmax)
    iy2 = min(a.ymax, b.ymax)
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih
    union = a.area + b.area - inter
    return float(inter / union) if union else 0.0


def solapes(cajas: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for stem, grupo in cajas.groupby("stem"):
        rows = list(grupo.itertuples(index=False))
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                a, b = rows[i], rows[j]
                sa = pd.Series(a._asdict())
                sb = pd.Series(b._asdict())
                filas.append(
                    {
                        "stem": stem,
                        "split": a.split,
                        "clase_a": a.clase,
                        "clase_b": b.clase,
                        "iou": iou(sa, sb),
                    }
                )
    return pd.DataFrame(filas)


def guardar_figura(nombre: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta = OUT_DIR / nombre
    plt.tight_layout()
    plt.savefig(ruta, dpi=120, bbox_inches="tight")
    plt.close()
    return ruta


def graficos(imagenes: pd.DataFrame, cajas: pd.DataFrame) -> None:
    inst = cajas["clase"].value_counts().reindex(["egg", "crack"])
    fig, ax = plt.subplots(figsize=(6, 4))
    inst.plot(kind="bar", ax=ax)
    ax.set_title("Instancias por clase")
    ax.set_xlabel("Clase")
    ax.set_ylabel("Cajas")
    guardar_figura("class_distribution.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    imagenes["n_objetos"].value_counts().sort_index().plot(kind="bar", ax=ax)
    ax.set_title("Objetos por imagen")
    ax.set_xlabel("Número de objetos")
    ax.set_ylabel("Imágenes")
    guardar_figura("objects_per_image.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    for clase in ("egg", "crack"):
        ax.hist(cajas.loc[cajas["clase"] == clase, "area_rel"].dropna(), bins=30, alpha=0.6, label=clase)
    ax.set_title("Área relativa de las cajas")
    ax.set_xlabel("Área caja / área imagen")
    ax.set_ylabel("Frecuencia")
    ax.legend()
    guardar_figura("bbox_area_distribution.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    res = imagenes.groupby(["width", "height"]).size().reset_index(name="n")
    etiquetas = [f"{int(r.width)}x{int(r.height)}" for r in res.itertuples()]
    ax.bar(etiquetas, res["n"])
    ax.set_title("Resoluciones")
    ax.set_ylabel("Imágenes")
    guardar_figura("resolution_distribution.png")

    fig, axes = plt.subplots(1, 2, figsize=(8, 4), sharex=True, sharey=True)
    for ax, clase in zip(axes, ("egg", "crack")):
        sub = cajas[cajas["clase"] == clase]
        ax.hist2d(sub["cx_rel"], sub["cy_rel"], bins=16, range=[[0, 1], [0, 1]])
        ax.set_title(f"Centro de caja: {clase}")
        ax.set_xlabel("x relativo")
        ax.set_ylabel("y relativo")
        ax.invert_yaxis()
    guardar_figura("bbox_center_heatmap.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    for split in ("train", "test"):
        ax.hist(
            cajas.loc[cajas["split"] == split, "area_rel"].dropna(),
            bins=25,
            alpha=0.5,
            density=True,
            label=split,
        )
    ax.set_title("Área relativa: train vs test")
    ax.set_xlabel("Área relativa")
    ax.set_ylabel("Densidad")
    ax.legend()
    guardar_figura("bbox_area_train_vs_test.png")


def dibujar_muestras(imagenes: pd.DataFrame, cajas: pd.DataFrame, rng: random.Random) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    colores = {"egg": (220, 50, 47), "crack": (38, 139, 210)}

    def pick(mask, k, label):
        cands = imagenes.loc[mask, "stem"].tolist()
        if not cands:
            return
        stems = rng.sample(cands, k=min(k, len(cands)))
        fig, axes = plt.subplots(1, len(stems), figsize=(4 * len(stems), 5))
        if len(stems) == 1:
            axes = [axes]
        for ax, stem in zip(axes, stems):
            fila = imagenes.loc[imagenes["stem"] == stem].iloc[0]
            img = Image.open(fila["jpg"]).convert("RGB")
            img.thumbnail((480, 640))
            sx = img.width / fila["width"]
            sy = img.height / fila["height"]
            draw = ImageDraw.Draw(img)
            for box in cajas[cajas["stem"] == stem].itertuples():
                color = colores.get(box.clase, (0, 0, 0))
                draw.rectangle(
                    [box.xmin * sx, box.ymin * sy, box.xmax * sx, box.ymax * sy],
                    outline=color,
                    width=3,
                )
                draw.text((box.xmin * sx + 2, box.ymin * sy + 2), box.clase, fill=color)
            ax.imshow(img)
            ax.set_title(f"{fila['split']} {stem}", fontsize=8)
            ax.axis("off")
        fig.suptitle(label)
        guardar_figura(f"samples_{label.replace(' ', '_')}.png")

    pick(imagenes["tiene_egg"] & ~imagenes["tiene_crack"], 3, "solo egg")
    pick(~imagenes["tiene_egg"] & imagenes["tiene_crack"], 2, "solo crack")
    pick(imagenes["tiene_egg"] & imagenes["tiene_crack"], 3, "ambas clases")
    pick(imagenes["n_objetos"] >= 4, 3, "muchos objetos")
    peq = set(cajas.loc[cajas["area_rel"] < 0.01, "stem"])
    pick(imagenes["stem"].isin(peq), 3, "cajas pequenas")


def brillo_muestra(imagenes: pd.DataFrame, rng: random.Random, n: int = 80) -> dict:
    """Media de luminancia en una muestra; no se leen las 840 fotos completas."""
    stems = imagenes["stem"].tolist()
    muestra = rng.sample(stems, k=min(n, len(stems)))
    valores = []
    for stem in muestra:
        fila = imagenes.loc[imagenes["stem"] == stem].iloc[0]
        with Image.open(fila["jpg"]) as im:
            gris = im.convert("L")
            gris.thumbnail((128, 128))
            arr = np.asarray(gris, dtype=np.float32)
            valores.append(float(arr.mean()))
    s = pd.Series(valores)
    return {
        "n": int(len(valores)),
        "min": float(s.min()),
        "max": float(s.max()),
        "media": float(s.mean()),
        "std": float(s.std()),
    }


def resumen(imagenes: pd.DataFrame, cajas: pd.DataFrame, meta: dict, ious: pd.DataFrame, brillo: dict) -> dict:
    n_img = int(len(imagenes))
    n_train = int((imagenes["split"] == "train").sum())
    n_test = int((imagenes["split"] == "test").sum())
    inst = cajas["clase"].value_counts().to_dict()
    imgs_egg = int(imagenes["tiene_egg"].sum())
    imgs_crack = int(imagenes["tiene_crack"].sum())
    ambas = int((imagenes["tiene_egg"] & imagenes["tiene_crack"]).sum())
    solo_egg = int((imagenes["tiene_egg"] & ~imagenes["tiene_crack"]).sum())
    solo_crack = int((~imagenes["tiene_egg"] & imagenes["tiene_crack"]).sum())
    sin_obj = int((imagenes["n_objetos"] == 0).sum())

    def split_stats(nombre: str) -> dict:
        img = imagenes[imagenes["split"] == nombre]
        box = cajas[cajas["split"] == nombre]
        return {
            "imagenes": int(len(img)),
            "objetos": int(len(box)),
            "objetos_por_imagen_media": float(img["n_objetos"].mean()) if len(img) else None,
            "pct_con_egg": float(img["tiene_egg"].mean() * 100) if len(img) else None,
            "pct_con_crack": float(img["tiene_crack"].mean() * 100) if len(img) else None,
            "area_rel_media": float(box["area_rel"].mean()) if len(box) else None,
            "resoluciones": {
                f"{int(w)}x{int(h)}": int(n)
                for (w, h), n in img.groupby(["width", "height"]).size().items()
            },
        }

    por_clase = {}
    for clase in ("egg", "crack"):
        sub = cajas[cajas["clase"] == clase]
        por_clase[clase] = {
            "instancias": int(len(sub)),
            "pct_instancias": float(len(sub) / len(cajas) * 100) if len(cajas) else 0,
            "bbox_w_media": float(sub["bbox_w"].mean()),
            "bbox_h_media": float(sub["bbox_h"].mean()),
            "area_rel_media": float(sub["area_rel"].mean()),
            "area_rel_mediana": float(sub["area_rel"].median()),
            "area_rel_min": float(sub["area_rel"].min()),
            "area_rel_max": float(sub["area_rel"].max()),
            "muy_pequenas": int((sub["area_rel"] < AREA_REL_MUY_PEQ).sum()),
            "muy_grandes": int((sub["area_rel"] > AREA_REL_MUY_GRANDE).sum()),
        }

    egg_crack = ious[(ious["clase_a"] != ious["clase_b"])] if len(ious) else ious
    return {
        "imagenes_total": n_img,
        "train": n_train,
        "test": n_test,
        "anotaciones_xml": n_img,
        "instancias_total": int(len(cajas)),
        "instancias_por_clase": {k: int(v) for k, v in inst.items()},
        "imagenes_con_egg": imgs_egg,
        "imagenes_con_crack": imgs_crack,
        "imagenes_ambas": ambas,
        "imagenes_solo_egg": solo_egg,
        "imagenes_solo_crack": solo_crack,
        "imagenes_sin_objetos": sin_obj,
        "objetos_por_imagen": {
            "media": float(imagenes["n_objetos"].mean()),
            "mediana": float(imagenes["n_objetos"].median()),
            "min": int(imagenes["n_objetos"].min()),
            "max": int(imagenes["n_objetos"].max()),
            "distribucion": {int(k): int(v) for k, v in imagenes["n_objetos"].value_counts().sort_index().items()},
        },
        "resoluciones": {
            f"{int(w)}x{int(h)}": int(n)
            for (w, h), n in imagenes.groupby(["width", "height"]).size().items()
        },
        "portrait": int((imagenes["height"] > imagenes["width"]).sum()),
        "landscape": int((imagenes["width"] > imagenes["height"]).sum()),
        "calidad": {
            "cajas_fuera": int(cajas["fuera"].sum()),
            "cajas_degeneradas": int(cajas["degenerada"].sum()),
            "muy_pequenas": int((cajas["area_rel"] < AREA_REL_MUY_PEQ).sum()),
            "muy_grandes": int((cajas["area_rel"] > AREA_REL_MUY_GRANDE).sum()),
            "xml_invalidos": meta["xml_invalidos"],
            "jpg_sin_xml": meta["jpg_sin_xml"],
            "xml_sin_jpg": meta["xml_sin_jpg"],
        },
        "iou_entre_clases": {
            "pares": int(len(egg_crack)),
            "iou_media": float(egg_crack["iou"].mean()) if len(egg_crack) else None,
            "iou_mediana": float(egg_crack["iou"].median()) if len(egg_crack) else None,
            "iou_gt_0_1": int((egg_crack["iou"] > 0.1).sum()) if len(egg_crack) else 0,
        },
        "por_clase": por_clase,
        "por_split": {"train": split_stats("train"), "test": split_stats("test")},
        "brillo_muestra": brillo,
    }


def imprimir(stats: dict) -> None:
    print("=" * 72)
    print("EDA INDIGO  (sin entrenar, sin convertir VOC→YOLO)")
    print("=" * 72)
    print(f"Imágenes reales:     {stats['imagenes_total']}  (train {stats['train']} / test {stats['test']})")
    print(f"XML:                 {stats['anotaciones_xml']}")
    print(f"Instancias:          {stats['instancias_total']}  {stats['instancias_por_clase']}")
    print(f"Imágenes con egg:    {stats['imagenes_con_egg']}")
    print(f"Imágenes con crack:  {stats['imagenes_con_crack']}")
    print(f"Ambas / solo egg / solo crack: {stats['imagenes_ambas']} / {stats['imagenes_solo_egg']} / {stats['imagenes_solo_crack']}")
    opi = stats["objetos_por_imagen"]
    print(f"Objetos/imagen:      media={opi['media']:.3f}  mediana={opi['mediana']:.1f}  min={opi['min']}  max={opi['max']}")
    print(f"Distribución:        {opi['distribucion']}")
    print(f"Resoluciones:        {stats['resoluciones']}  portrait={stats['portrait']} landscape={stats['landscape']}")
    print(f"Calidad:             {stats['calidad']}")
    print(f"IoU egg-crack:       {stats['iou_entre_clases']}")
    print("Por clase:")
    for clase, d in stats["por_clase"].items():
        print(f"  {clase}: {d}")
    print("Train vs test:")
    for nombre, d in stats["por_split"].items():
        print(f"  {nombre}: {d}")
    print(f"Brillo (muestra):    {stats['brillo_muestra']}")
    print(f"Figuras:             {OUT_DIR}")


def main() -> int:
    configurar_salida()
    parser = argparse.ArgumentParser(description="EDA de INDIGO (solo lectura).")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    np.random.seed(args.seed)

    imagenes, cajas, meta = cargar()
    ious = solapes(cajas)
    brillo = brillo_muestra(imagenes, rng)
    graficos(imagenes, cajas)
    dibujar_muestras(imagenes, cajas, rng)
    stats = resumen(imagenes, cajas, meta, ious, brillo)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    imprimir(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
