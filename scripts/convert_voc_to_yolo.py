#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convierte INDIGO (Pascal VOC) a formato YOLOv8.

Lee únicamente:
  data/raw/indigo/train/train_100/
  data/raw/indigo/test/test_100/

Escribe en:
  data/processed/indigo_yolo/

No modifica data/raw/indigo/. No entrena. No redimensiona. No augmentation.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parents[1]
INDIGO_RAW = REPO_ROOT / "data" / "raw" / "indigo"
RAW_SPLITS = {
    "train_orig": INDIGO_RAW / "train" / "train_100",
    "test_orig": INDIGO_RAW / "test" / "test_100",
}
OUT_ROOT = REPO_ROOT / "data" / "processed" / "indigo_yolo"
VIS_DIR = REPO_ROOT / "evaluation" / "yolo_conversion"

SEED = 42
TRAIN_RATIO = 0.85
CLASS_MAP = {"egg": 0, "crack": 1}
CLASS_NAMES = {0: "egg", 1: "crack"}
TOLERANCE_PX = 2.0
N_COMPARE = 8
N_VIS = 6


@dataclass
class BoxVOC:
    clase: str
    xmin: float
    ymin: float
    xmax: float
    ymax: float


@dataclass
class BoxYOLO:
    class_id: int
    x_center: float
    y_center: float
    width: float
    height: float


@dataclass
class ConversionReport:
    split_counts: dict[str, int] = field(default_factory=dict)
    label_counts: dict[str, int] = field(default_factory=dict)
    class_distribution: dict[str, Counter] = field(default_factory=dict)
    validation: dict = field(default_factory=dict)
    comparison: list[dict] = field(default_factory=list)
    copy_bytes: int = 0
    raw_snapshot: dict = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)


def configurar_salida() -> None:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def es_auxiliar(ruta: Path) -> bool:
    if ruta.name.startswith("._") or ruta.name in {".DS_Store", "_extracted.ok"}:
        return True
    return "__MACOSX" in ruta.parts


def parsear_xml(xml_path: Path) -> tuple[int, int, list[BoxVOC]]:
    try:
        raiz = ET.parse(xml_path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"XML inválido: {xml_path}") from exc

    width = int(float(raiz.findtext("size/width") or 0))
    height = int(float(raiz.findtext("size/height") or 0))
    if width <= 0 or height <= 0:
        raise ValueError(f"Dimensiones inválidas en {xml_path}: {width}x{height}")

    boxes: list[BoxVOC] = []
    for obj in raiz.findall("object"):
        nombre = (obj.findtext("name") or "").strip()
        if nombre not in CLASS_MAP:
            raise ValueError(
                f"Clase desconocida '{nombre}' en {xml_path}. "
                f"Clases permitidas: {sorted(CLASS_MAP)}"
            )
        bb = obj.find("bndbox")
        if bb is None:
            continue
        boxes.append(
            BoxVOC(
                clase=nombre,
                xmin=float(bb.findtext("xmin") or 0),
                ymin=float(bb.findtext("ymin") or 0),
                xmax=float(bb.findtext("xmax") or 0),
                ymax=float(bb.findtext("ymax") or 0),
            )
        )
    return width, height, boxes


def voc_a_yolo(box: BoxVOC, img_w: int, img_h: int) -> BoxYOLO:
    x_center = ((box.xmin + box.xmax) / 2.0) / img_w
    y_center = ((box.ymin + box.ymax) / 2.0) / img_h
    width = (box.xmax - box.xmin) / img_w
    height = (box.ymax - box.ymin) / img_h
    return BoxYOLO(
        class_id=CLASS_MAP[box.clase],
        x_center=x_center,
        y_center=y_center,
        width=width,
        height=height,
    )


def yolo_a_pixels(box: BoxYOLO, img_w: int, img_h: int) -> tuple[float, float, float, float]:
    w = box.width * img_w
    h = box.height * img_h
    cx = box.x_center * img_w
    cy = box.y_center * img_h
    xmin = cx - w / 2.0
    ymin = cy - h / 2.0
    xmax = xmin + w
    ymax = ymin + h
    return xmin, ymin, xmax, ymax


def listar_pares(carpeta: Path) -> list[tuple[Path, Path]]:
    jpgs = {
        p.stem: p
        for p in sorted(carpeta.glob("*.jpg"))
        if p.is_file() and not es_auxiliar(p)
    }
    xmls = {
        p.stem: p
        for p in sorted(carpeta.glob("*.xml"))
        if p.is_file() and not es_auxiliar(p)
    }
    faltantes_jpg = sorted(set(xmls) - set(jpgs))
    faltantes_xml = sorted(set(jpgs) - set(xmls))
    if faltantes_jpg or faltantes_xml:
        msg = []
        if faltantes_xml:
            msg.append(f"JPG sin XML: {faltantes_xml[:5]}")
        if faltantes_jpg:
            msg.append(f"XML sin JPG: {faltantes_jpg[:5]}")
        raise RuntimeError(f"Pares incompletos en {carpeta}: {'; '.join(msg)}")

    return [(jpgs[stem], xmls[stem]) for stem in sorted(jpgs)]


def estimar_bytes_copia(pares: list[tuple[Path, Path]]) -> int:
    return sum(jpg.stat().st_size for jpg, _ in pares)


def snapshot_raw() -> dict:
    info: dict[str, dict] = {}
    for nombre, carpeta in RAW_SPLITS.items():
        jpgs = [
            p
            for p in carpeta.glob("*.jpg")
            if p.is_file() and not es_auxiliar(p)
        ]
        xmls = [
            p
            for p in carpeta.glob("*.xml")
            if p.is_file() and not es_auxiliar(p)
        ]
        info[nombre] = {
            "jpg_count": len(jpgs),
            "xml_count": len(xmls),
            "bytes_jpg": sum(p.stat().st_size for p in jpgs),
            "newest_mtime": max((p.stat().st_mtime for p in jpgs + xmls), default=0),
        }
    return info


def dividir_train_val(
    pares_train: list[tuple[Path, Path]], seed: int, ratio: float
) -> tuple[list[tuple[Path, Path]], list[tuple[Path, Path]]]:
    items = list(pares_train)
    rng = random.Random(seed)
    rng.shuffle(items)
    n_train = int(round(len(items) * ratio))
    return items[:n_train], items[n_train:]


def escribir_label(path: Path, boxes: list[BoxYOLO]) -> None:
    lineas = [
        f"{b.class_id} {b.x_center:.6f} {b.y_center:.6f} {b.width:.6f} {b.height:.6f}"
        for b in boxes
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lineas) + ("\n" if lineas else ""), encoding="utf-8")


def leer_label(path: Path) -> list[BoxYOLO]:
    boxes: list[BoxYOLO] = []
    if not path.exists():
        return boxes
    for i, linea in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        partes = linea.strip().split()
        if not partes:
            continue
        if len(partes) != 5:
            raise ValueError(f"Formato inválido en {path}:{i}: {linea!r}")
        cid = int(partes[0])
        if cid not in CLASS_NAMES:
            raise ValueError(f"Clase inválida {cid} en {path}:{i}")
        boxes.append(
            BoxYOLO(
                class_id=cid,
                x_center=float(partes[1]),
                y_center=float(partes[2]),
                width=float(partes[3]),
                height=float(partes[4]),
            )
        )
    return boxes


def copiar_y_convertir(
    split: str,
    pares: list[tuple[Path, Path]],
    report: ConversionReport,
) -> list[tuple[Path, Path, list[BoxVOC], list[BoxYOLO], int, int]]:
    img_dir = OUT_ROOT / "images" / split
    lbl_dir = OUT_ROOT / "labels" / split
    img_dir.mkdir(parents=True, exist_ok=True)
    lbl_dir.mkdir(parents=True, exist_ok=True)

    registros = []
    for jpg, xml in pares:
        img_w, img_h, boxes_voc = parsear_xml(xml)
        boxes_yolo = [voc_a_yolo(b, img_w, img_h) for b in boxes_voc]

        dst_img = img_dir / jpg.name
        dst_lbl = lbl_dir / f"{jpg.stem}.txt"

        shutil.copy2(jpg, dst_img)
        report.copy_bytes += jpg.stat().st_size
        escribir_label(dst_lbl, boxes_yolo)

        for b in boxes_yolo:
            report.class_distribution[split][CLASS_NAMES[b.class_id]] += 1

        registros.append((dst_img, dst_lbl, boxes_voc, boxes_yolo, img_w, img_h))

    report.split_counts[split] = len(pares)
    report.label_counts[split] = len(list(lbl_dir.glob("*.txt")))
    return registros


def crear_data_yaml() -> None:
    contenido = (
        "# INDIGO Crack Detection — YOLOv8\n"
        "# Actualizar `path` en Colab si el dataset se copia a otra ubicación.\n"
        f"path: {OUT_ROOT.as_posix()}\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        "nc: 2\n"
        "names:\n"
        "  0: egg\n"
        "  1: crack\n"
    )
    (OUT_ROOT / "data.yaml").write_text(contenido, encoding="utf-8")


def validar_dataset(report: ConversionReport) -> bool:
    ok = True
    val: dict = {
        "images_without_label": [],
        "labels_without_image": [],
        "coords_out_of_range": [],
        "invalid_width_height": [],
        "invalid_classes": [],
    }

    for split in ("train", "val", "test"):
        img_dir = OUT_ROOT / "images" / split
        lbl_dir = OUT_ROOT / "labels" / split
        imgs = {p.stem for p in img_dir.glob("*.jpg")}
        lbls = {p.stem for p in lbl_dir.glob("*.txt")}

        for stem in sorted(imgs - lbls):
            val["images_without_label"].append(f"{split}/{stem}.jpg")
            ok = False
        for stem in sorted(lbls - imgs):
            val["labels_without_image"].append(f"{split}/{stem}.txt")
            ok = False

        for lbl in lbl_dir.glob("*.txt"):
            for i, box in enumerate(leer_label(lbl), start=1):
                if box.class_id not in CLASS_NAMES:
                    val["invalid_classes"].append(f"{lbl}:{i} class={box.class_id}")
                    ok = False
                if box.width <= 0 or box.height <= 0:
                    val["invalid_width_height"].append(
                        f"{lbl.relative_to(OUT_ROOT)}:{i} w={box.width} h={box.height}"
                    )
                    ok = False
                for nombre, valor in (
                    ("x_center", box.x_center),
                    ("y_center", box.y_center),
                    ("width", box.width),
                    ("height", box.height),
                ):
                    if valor < 0 or valor > 1:
                        val["coords_out_of_range"].append(
                            f"{lbl.relative_to(OUT_ROOT)}:{i} {nombre}={valor}"
                        )
                        ok = False

    val["image_counts"] = {
        s: len(list((OUT_ROOT / "images" / s).glob("*.jpg")))
        for s in ("train", "val", "test")
    }
    val["label_counts"] = {
        s: len(list((OUT_ROOT / "labels" / s).glob("*.txt")))
        for s in ("train", "val", "test")
    }

    for split in ("train", "val", "test"):
        clases = set(report.class_distribution[split])
        val[f"{split}_has_egg_and_crack"] = {"egg", "crack"}.issubset(clases)

    report.validation = val
    return ok


def comparar_voc_yolo(
    registros_por_split: dict[str, list],
    report: ConversionReport,
    n: int,
    seed: int,
) -> bool:
    pool = []
    for split, regs in registros_por_split.items():
        for reg in regs:
            pool.append((split, reg))

    rng = random.Random(seed)
    muestra = rng.sample(pool, min(n, len(pool)))
    todo_ok = True

    for split, (img_path, _, boxes_voc, boxes_yolo, img_w, img_h) in muestra:
        if len(boxes_voc) != len(boxes_yolo):
            todo_ok = False
            report.comparison.append(
                {
                    "split": split,
                    "image": img_path.name,
                    "ok": False,
                    "error": f"conteo distinto VOC={len(boxes_voc)} YOLO={len(boxes_yolo)}",
                }
            )
            continue

        voc_sorted = sorted(
            boxes_voc, key=lambda b: (CLASS_MAP[b.clase], b.xmin, b.ymin)
        )
        yolo_sorted = sorted(
            boxes_yolo, key=lambda b: (b.class_id, b.x_center, b.y_center)
        )

        max_diff = 0.0
        for vb, yb in zip(voc_sorted, yolo_sorted):
            px = yolo_a_pixels(yb, img_w, img_h)
            diffs = [
                abs(vb.xmin - px[0]),
                abs(vb.ymin - px[1]),
                abs(vb.xmax - px[2]),
                abs(vb.ymax - px[3]),
            ]
            max_diff = max(max_diff, *diffs)

        ok = max_diff <= TOLERANCE_PX
        if not ok:
            todo_ok = False
        report.comparison.append(
            {
                "split": split,
                "image": img_path.name,
                "objects": len(boxes_voc),
                "max_diff_px": round(max_diff, 4),
                "ok": ok,
            }
        )

    return todo_ok


def dibujar_visualizaciones(
    registros_por_split: dict[str, list],
    n: int,
    seed: int,
) -> None:
    VIS_DIR.mkdir(parents=True, exist_ok=True)
    pool = []
    for split, regs in registros_por_split.items():
        for reg in regs:
            pool.append((split, reg))
    rng = random.Random(seed + 1)
    muestra = rng.sample(pool, min(n, len(pool)))

    colores = {0: (0, 200, 0), 1: (220, 40, 40)}

    for split, (img_path, _, _, boxes_yolo, img_w, img_h) in muestra:
        img = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        for box in boxes_yolo:
            xmin, ymin, xmax, ymax = yolo_a_pixels(box, img_w, img_h)
            color = colores[box.class_id]
            draw.rectangle([xmin, ymin, xmax, ymax], outline=color, width=4)
            draw.text(
                (xmin + 4, max(0, ymin - 18)),
                CLASS_NAMES[box.class_id],
                fill=color,
            )
        out = VIS_DIR / f"{split}_{img_path.stem}_yolo.png"
        img.save(out, format="PNG")
        plt.close("all")


def verificar_raw_intacto(antes: dict, despues: dict) -> bool:
    return antes == despues


def limpiar_salida(force: bool) -> None:
    if OUT_ROOT.exists():
        if not force:
            raise RuntimeError(
                f"La salida {OUT_ROOT} ya existe. Use --force para regenerar."
            )
        shutil.rmtree(OUT_ROOT)
    if VIS_DIR.exists() and force:
        for p in VIS_DIR.glob("*"):
            if p.is_file():
                p.unlink()


def main() -> int:
    configurar_salida()
    parser = argparse.ArgumentParser(description="Convierte INDIGO VOC a YOLOv8")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerar data/processed/indigo_yolo/ si ya existe",
    )
    args = parser.parse_args()

    report = ConversionReport(
        class_distribution={s: Counter() for s in ("train", "val", "test")}
    )

    print("=== INDIGO VOC -> YOLO ===")
    print(f"Seed: {SEED}")
    print(f"Train ratio (desde train original): {TRAIN_RATIO}")

    raw_antes = snapshot_raw()
    report.raw_snapshot["before"] = raw_antes

    pares_train_orig = listar_pares(RAW_SPLITS["train_orig"])
    pares_test_orig = listar_pares(RAW_SPLITS["test_orig"])
    print(f"Train original: {len(pares_train_orig)} pares")
    print(f"Test original:  {len(pares_test_orig)} pares")

    bytes_estimados = estimar_bytes_copia(pares_train_orig + pares_test_orig)
    print(
        f"Espacio adicional estimado por copia de imágenes: "
        f"{bytes_estimados / (1024**3):.3f} GiB ({bytes_estimados:,} bytes)"
    )

    pares_train, pares_val = dividir_train_val(pares_train_orig, SEED, TRAIN_RATIO)
    print(f"Split resultante: train={len(pares_train)}, val={len(pares_val)}, test={len(pares_test_orig)}")

    limpiar_salida(args.force)

    registros: dict[str, list] = {}
    registros["train"] = copiar_y_convertir("train", pares_train, report)
    registros["val"] = copiar_y_convertir("val", pares_val, report)
    registros["test"] = copiar_y_convertir("test", pares_test_orig, report)

    crear_data_yaml()

    val_ok = validar_dataset(report)
    cmp_ok = comparar_voc_yolo(registros, report, N_COMPARE, SEED)
    dibujar_visualizaciones(registros, N_VIS, SEED)

    raw_despues = snapshot_raw()
    report.raw_snapshot["after"] = raw_despues
    raw_ok = verificar_raw_intacto(raw_antes, raw_despues)

    print("\n=== Conteos finales ===")
    for split in ("train", "val", "test"):
        print(
            f"  {split}: {report.validation['image_counts'][split]} imgs, "
            f"{report.validation['label_counts'][split]} labels"
        )

    print("\n=== Distribución de instancias por split ===")
    for split in ("train", "val", "test"):
        c = report.class_distribution[split]
        print(f"  {split}: egg={c['egg']}, crack={c['crack']}")

    print("\n=== Validación ===")
    print(f"  Pares imagen/label OK: {val_ok}")
    print(f"  Comparación VOC vs YOLO OK (tol={TOLERANCE_PX}px): {cmp_ok}")
    print(f"  data/raw/indigo/ intacto: {raw_ok}")
    print(
        f"  Espacio copiado: {report.copy_bytes / (1024**3):.3f} GiB "
        f"({report.copy_bytes:,} bytes)"
    )

    if report.validation["coords_out_of_range"]:
        print(f"  Coordenadas fuera de rango: {len(report.validation['coords_out_of_range'])}")
    if report.validation["invalid_width_height"]:
        print(f"  width/height inválidos: {len(report.validation['invalid_width_height'])}")

    print("\n=== Comparación VOC vs YOLO (muestra) ===")
    for item in report.comparison:
        estado = "OK" if item.get("ok") else "FAIL"
        detalle = item.get("max_diff_px", item.get("error", ""))
        print(f"  [{estado}] {item['split']}/{item['image']}: {detalle}")

    summary_path = VIS_DIR / "conversion_summary.json"
    VIS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(
            {
                "seed": SEED,
                "train_ratio": TRAIN_RATIO,
                "split_counts": report.split_counts,
                "class_distribution": {
                    k: dict(v) for k, v in report.class_distribution.items()
                },
                "validation": report.validation,
                "comparison": report.comparison,
                "copy_bytes": report.copy_bytes,
                "raw_intact": raw_ok,
                "ready": val_ok and cmp_ok and raw_ok,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"\nResumen JSON: {summary_path}")

    listo = val_ok and cmp_ok and raw_ok
    print("\n=== RESULTADO ===")
    print("LISTO PARA ENTRENAMIENTO YOLOV8" if listo else "NO LISTO")
    return 0 if listo else 1


if __name__ == "__main__":
    raise SystemExit(main())
