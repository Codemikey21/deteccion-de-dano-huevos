#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Descarga el conjunto INDIGO Crack Detection desde figshare a data/raw/indigo/.

Conjunto: Dataset for real-time crack detection on chicken eggs
DOI: 10.6084/m9.figshare.21568425.v1
Autores: Bhavya Botta y Ashis Kumar Datta
Licencia: CC BY 4.0 (verificada el 21/09/2026 contra la API de figshare)
Uso: dataset principal inicial de detección (`egg`) y de grieta (`crack`).

Este script SOLO descarga y descomprime los ZIP oficiales. Deliberadamente NO hace
nada de lo siguiente:
  - no transforma, redimensiona ni convierte imágenes;
  - no reetiqueta ni fusiona clases;
  - no entrena nada;
  - no borra archivos ya completos.

No requiere dependencias externas: usa solo la biblioteca estándar de Python.

Uso:
    python scripts/download_indigo_dataset.py --dry-run     # consultar sin descargar
    python scripts/download_indigo_dataset.py               # descargar lo que falte
    python scripts/download_indigo_dataset.py --verify-only # comprobar lo ya descargado
    python scripts/download_indigo_dataset.py --force       # re-descargar y re-extraer

Códigos de salida:
    0  correcto
    1  error de red o de verificación
    2  hay archivos locales en conflicto (use --force para sobrescribirlos)
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import sys
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ARTICLE_ID = 21568425
DOI = "10.6084/m9.figshare.21568425.v1"
ARTICLE_API = f"https://api.figshare.com/v2/articles/{ARTICLE_ID}"
LICENSE = "CC BY 4.0"
TITLE = "Dataset for real-time crack detection on chicken eggs"
AUTHORS = "Bhavya Botta; Ashis Kumar Datta"

# Recuento declarado por la ficha oficial (API figshare, 21/09/2026).
IMAGENES_DECLARADAS = 840
TRAIN_DECLARADAS = 740
TEST_DECLARADAS = 100

# Bytes de los ZIP únicos según la misma consulta. test.zip aparece dos veces
# en los metadatos con id distinto y el mismo MD5; el script se queda con uno.
ZIP_ESPERADOS = {
    "train.zip": {
        "size": 1_948_036_678,
        "md5": "6bdc229bc98c808ad7ec3f76e0e5feeb",
    },
    "test.zip": {
        "size": 266_920_567,
        "md5": "0d1bca3b8408cd7114cbcf0c6836c34b",
    },
}

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_DIR = REPO_ROOT / "data" / "raw" / "indigo"
MANIFEST_PATH = TARGET_DIR / "_manifest.json"

USER_AGENT = "deteccion-huevos-uab/0.1 (proyecto academico; urllib)"
CHUNK = 1 << 20  # 1 MiB
RETRYABLE_HTTP = {408, 425, 429, 500, 502, 503, 504}
EXTENSIONES_IMAGEN = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def es_imagen(ruta: Path) -> bool:
    return ruta.suffix.lower() in EXTENSIONES_IMAGEN


def configurar_salida() -> None:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def tam(n: int) -> str:
    valor = float(n)
    for unidad in ("B", "KiB", "MiB", "GiB"):
        if valor < 1024 or unidad == "GiB":
            return f"{valor:.2f} {unidad}" if unidad != "B" else f"{int(valor)} B"
        valor /= 1024
    return f"{valor:.2f} GiB"


def titulo(texto: str) -> None:
    print()
    print(texto)
    print("-" * len(texto))


def barra(prefijo: str, hechos: int, total: int) -> None:
    if total > 0:
        pct = hechos / total * 100
        llenos = int(24 * hechos / total)
        marca = "#" * llenos + "." * (24 - llenos)
        linea = f"  {prefijo} [{marca}] {pct:5.1f}%  {tam(hechos)}/{tam(total)}"
    else:
        linea = f"  {prefijo} {tam(hechos)}"
    sys.stdout.write("\r" + linea.ljust(96))
    sys.stdout.flush()


def abrir(url: str, timeout: int, headers: dict | None = None):
    cabeceras = {"User-Agent": USER_AGENT}
    if headers:
        cabeceras.update(headers)
    peticion = urllib.request.Request(url, headers=cabeceras)
    return urllib.request.urlopen(peticion, timeout=timeout)


def con_reintentos(accion, descripcion: str, reintentos: int):
    ultimo_error: Exception | None = None
    for intento in range(1, reintentos + 1):
        try:
            return accion()
        except urllib.error.HTTPError as exc:
            ultimo_error = exc
            if exc.code not in RETRYABLE_HTTP:
                raise RuntimeError(
                    f"{descripcion}: el servidor respondió HTTP {exc.code} ({exc.reason}). "
                    "No se reintenta porque es un error definitivo."
                ) from exc
        except urllib.error.URLError as exc:
            ultimo_error = exc
        except (TimeoutError, ConnectionError, http.client.IncompleteRead) as exc:
            ultimo_error = exc

        if intento < reintentos:
            espera = 2 ** intento
            print(f"    Fallo de red ({ultimo_error}). Reintento {intento}/{reintentos - 1} "
                  f"en {espera} s...")
            time.sleep(espera)

    raise RuntimeError(
        f"{descripcion}: agotados {reintentos} intentos. Último error: {ultimo_error}"
    )


def consultar_articulo(timeout: int, reintentos: int) -> dict:
    def _pedir():
        with abrir(ARTICLE_API, timeout) as respuesta:
            return json.loads(respuesta.read().decode("utf-8"))

    return con_reintentos(_pedir, "Consulta de metadatos de figshare", reintentos)


def archivos_unicos(articulo: dict) -> tuple[list[dict], list[dict]]:
    """Devuelve (archivos_a_descargar, duplicados_omitidos)."""
    vistos: dict[tuple[str, int, str], dict] = {}
    duplicados: list[dict] = []
    for entrada in articulo.get("files") or []:
        nombre = entrada.get("name") or ""
        tamano = int(entrada.get("size") or 0)
        md5 = (entrada.get("computed_md5") or entrada.get("supplied_md5") or "").lower()
        clave = (nombre, tamano, md5)
        registro = {
            "id": int(entrada["id"]),
            "name": nombre,
            "size": tamano,
            "md5": md5,
            "download_url": entrada.get("download_url")
            or f"https://ndownloader.figshare.com/files/{entrada['id']}",
        }
        if clave in vistos:
            duplicados.append(registro)
            continue
        vistos[clave] = registro
    return list(vistos.values()), duplicados


def md5_archivo(ruta: Path) -> str:
    h = hashlib.md5()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(CHUNK), b""):
            h.update(bloque)
    return h.hexdigest()


def clasificar(archivos: list[dict], destino: Path) -> tuple[list, list, list]:
    faltantes, presentes, conflictos = [], [], []
    for archivo in archivos:
        local = destino / archivo["name"]
        if not local.exists():
            faltantes.append(archivo)
        elif local.stat().st_size == archivo["size"]:
            presentes.append(archivo)
        else:
            conflictos.append((archivo, local.stat().st_size))
    return faltantes, presentes, conflictos


def descargar_uno(archivo: dict, destino: Path, timeout: int, reintentos: int,
                  etiqueta: str) -> None:
    """Descarga a un .part y solo entonces renombra. Reanuda si hay .part."""
    final = destino / archivo["name"]
    parcial = final.with_name(final.name + ".part")
    destino.mkdir(parents=True, exist_ok=True)

    def _bajar():
        ya = parcial.stat().st_size if parcial.exists() else 0
        if ya > archivo["size"]:
            parcial.unlink()
            ya = 0
        cabeceras = {}
        modo = "wb"
        if ya:
            cabeceras["Range"] = f"bytes={ya}-"
            modo = "ab"
        with abrir(archivo["download_url"], timeout, cabeceras) as respuesta:
            codigo = getattr(respuesta, "status", None) or respuesta.getcode()
            if ya and codigo == 200:
                respuesta.close()
                parcial.unlink(missing_ok=True)
                ya = 0
                modo = "wb"
                respuesta = abrir(archivo["download_url"], timeout)
            descargados = ya
            with parcial.open(modo) as salida:
                while True:
                    bloque = respuesta.read(CHUNK)
                    if not bloque:
                        break
                    salida.write(bloque)
                    descargados += len(bloque)
                    barra(etiqueta, descargados, archivo["size"])
        sys.stdout.write("\r" + " " * 96 + "\r")
        sys.stdout.flush()
        return descargados

    try:
        descargados = con_reintentos(_bajar, f"Descarga de {archivo['name']}", reintentos)
        if descargados != archivo["size"]:
            raise RuntimeError(
                f"tamaño incorrecto: se esperaban {archivo['size']} bytes y llegaron {descargados}"
            )
        digest = md5_archivo(parcial)
        if archivo["md5"] and digest != archivo["md5"]:
            raise RuntimeError(
                f"MD5 distinto al de figshare (local {digest}, origen {archivo['md5']})"
            )
        parcial.replace(final)
    except Exception:
        if parcial.exists() and archivo["size"] and parcial.stat().st_size >= archivo["size"]:
            # ZIP completo pero inválido: no sirve para reanudar.
            parcial.unlink(missing_ok=True)
        raise


def extraer_zip(archivo: dict, destino: Path, force: bool) -> Path:
    zip_path = destino / archivo["name"]
    carpeta = destino / Path(archivo["name"]).stem
    marca = carpeta / "_extracted.ok"
    if marca.exists() and not force:
        return carpeta
    carpeta.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            nombre = info.filename.replace("\\", "/")
            if nombre.startswith("/") or ".." in Path(nombre).parts:
                raise RuntimeError(f"ruta insegura dentro de {archivo['name']}: {nombre}")
            zf.extract(info, carpeta)
    marca.write_text("ok\n", encoding="ascii")
    return carpeta


def contar_imagenes(destino: Path) -> dict:
    if not destino.exists():
        return {"total": 0, "por_carpeta": {}, "bytes": 0}
    por_carpeta: dict[str, int] = {}
    total = 0
    total_bytes = 0
    for ruta in destino.rglob("*"):
        if not ruta.is_file():
            continue
        if ruta.name.endswith(".part") or ruta.name in {"README.md", "_manifest.json", "_extracted.ok"}:
            continue
        if ruta.suffix.lower() == ".zip":
            continue
        if not es_imagen(ruta):
            continue
        total += 1
        total_bytes += ruta.stat().st_size
        rel = ruta.relative_to(destino).as_posix()
        if rel.startswith("train"):
            clave = "train"
        elif rel.startswith("test"):
            clave = "test"
        else:
            clave = str(ruta.parent.relative_to(destino).as_posix() or ".")
        por_carpeta[clave] = por_carpeta.get(clave, 0) + 1
    return {
        "total": total,
        "por_carpeta": dict(sorted(por_carpeta.items())),
        "bytes": total_bytes,
    }


def verificar_zips(archivos: list[dict], destino: Path, comprobar_hash: bool) -> tuple[list, list]:
    ausentes, corruptos = [], []
    for archivo in archivos:
        local = destino / archivo["name"]
        if not local.exists():
            ausentes.append(archivo["name"])
            continue
        if local.stat().st_size != archivo["size"]:
            corruptos.append((archivo["name"], "tamaño distinto al de figshare"))
            continue
        if comprobar_hash and archivo["md5"]:
            print(f"  MD5 {archivo['name']}...")
            if md5_archivo(local) != archivo["md5"]:
                corruptos.append((archivo["name"], "MD5 distinto al de figshare"))
    return ausentes, corruptos


def escribir_manifiesto(articulo: dict, archivos: list[dict], duplicados: list[dict],
                        resumen: dict, verificacion: dict) -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    contenido = {
        "dataset": TITLE,
        "doi": DOI,
        "url": f"https://doi.org/{DOI}",
        "figshare_article_id": ARTICLE_ID,
        "licencia": LICENSE,
        "autores": AUTHORS,
        "consultado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "imagenes_declaradas": IMAGENES_DECLARADAS,
        "train_declaradas": TRAIN_DECLARADAS,
        "test_declaradas": TEST_DECLARADAS,
        "archivos_descargados": archivos,
        "duplicados_omitidos": duplicados,
        "verificacion": verificacion,
        "resumen_local": resumen,
        "version_publicada": articulo.get("published_date"),
    }
    MANIFEST_PATH.write_text(
        json.dumps(contenido, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\n  Manifiesto escrito en {MANIFEST_PATH.relative_to(REPO_ROOT)}")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Descarga INDIGO Crack Detection (figshare, CC BY 4.0) "
                    "a data/raw/indigo/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="consulta metadatos y muestra qué se descargaría, sin escribir nada")
    parser.add_argument("--verify-only", action="store_true",
                        help="verifica los ZIP ya descargados y termina, sin descargar")
    parser.add_argument("--force", action="store_true",
                        help="re-descarga y vuelve a extraer, sobrescribiendo ZIP existentes")
    parser.add_argument("--check-hash", action="store_true",
                        help="al verificar, recalcula el MD5 de cada ZIP")
    parser.add_argument("--timeout", type=int, default=120,
                        help="tiempo máximo de espera por petición, en segundos")
    parser.add_argument("--retries", type=int, default=4,
                        help="número total de intentos ante fallos de red")
    return parser


def main() -> int:
    configurar_salida()
    args = construir_parser().parse_args()

    print("=" * 78)
    print(f"  Conjunto: {TITLE}")
    print(f"  DOI:      {DOI}")
    print(f"  Licencia: {LICENSE}")
    print(f"  Destino:  {TARGET_DIR.relative_to(REPO_ROOT).as_posix()}/")
    print("=" * 78)

    titulo("Consultando metadatos de figshare")
    try:
        articulo = consultar_articulo(args.timeout, args.retries)
    except RuntimeError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    print(f"  Título:    {articulo.get('title')}")
    licencia = (articulo.get("license") or {}).get("name")
    print(f"  Licencia:  {licencia}")
    print(f"  Publicado: {articulo.get('published_date')}")

    archivos, duplicados = archivos_unicos(articulo)
    if not archivos:
        print("\nERROR: figshare no devolvió archivos.", file=sys.stderr)
        return 1

    bytes_totales = sum(a["size"] for a in archivos)
    print(f"  ZIP únicos: {len(archivos)}  ({tam(bytes_totales)})")
    for archivo in archivos:
        print(f"    {archivo['name']:<12} id={archivo['id']}  {tam(archivo['size'])}  md5={archivo['md5']}")
    if duplicados:
        print(f"  Duplicados omitidos: {len(duplicados)}")
        for dup in duplicados:
            print(f"    {dup['name']} id={dup['id']} (mismo nombre, tamaño y MD5)")

    for archivo in archivos:
        esperado = ZIP_ESPERADOS.get(archivo["name"])
        if esperado and (archivo["size"] != esperado["size"] or archivo["md5"] != esperado["md5"]):
            print(
                f"\nAVISO: {archivo['name']} no coincide con los metadatos consultados "
                f"el 21/09/2026 (size {esperado['size']}, md5 {esperado['md5']}).",
                file=sys.stderr,
            )

    faltantes, presentes, conflictos = clasificar(archivos, TARGET_DIR)

    titulo("Estado local")
    print(f"  Ya presentes y del tamaño esperado: {len(presentes)}")
    print(f"  Por descargar:                      {len(faltantes)}")
    print(f"  En conflicto:                       {len(conflictos)}")
    print(f"  Espacio de los ZIP:                 {tam(bytes_totales)}")
    print("  Espacio recomendado (ZIP + extraído): ~6 GiB libres")

    if conflictos:
        print("\n  Estos ZIP existen con un tamaño distinto al de figshare.")
        print("  NO se sobrescriben. Revíselos y use --force si desea reemplazarlos:")
        for archivo, tamano_local in conflictos:
            print(f"    {archivo['name']}  (local {tam(tamano_local)}, origen {tam(archivo['size'])})")

    if args.verify_only:
        titulo("Verificación")
        ausentes, corruptos = verificar_zips(archivos, TARGET_DIR, args.check_hash)
        if not ausentes and not corruptos:
            print("  ZIP: presentes y del tamaño esperado.")
            resumen = contar_imagenes(TARGET_DIR)
            print(f"  Imágenes encontradas tras extraer: {resumen['total']} "
                  f"(declaradas: {IMAGENES_DECLARADAS})")
            for carpeta, n in resumen["por_carpeta"].items():
                print(f"    {carpeta}: {n}")
            return 0
        for ruta in ausentes:
            print(f"  FALTA:    {ruta}")
        for ruta, motivo in corruptos:
            print(f"  PROBLEMA: {ruta} -> {motivo}")
        return 1

    if args.dry_run:
        titulo("Simulación (--dry-run): no se ha escrito nada")
        pendientes = archivos if args.force else faltantes
        print(f"  Se descargarían {len(pendientes)} ZIP ({tam(sum(a['size'] for a in pendientes))})")
        print(f"  Tras la descarga se extraerían a data/raw/indigo/train/ y .../test/")
        print("  No se modificarían imágenes ni se entrenaría nada.")
        return 2 if conflictos and not args.force else 0

    if conflictos and not args.force:
        print("\nERROR: hay conflictos. No se ha descargado nada. Use --force para sobrescribir.",
              file=sys.stderr)
        return 2

    cola = archivos if args.force else faltantes
    if not cola:
        print("\n  No hay ZIP pendientes: los archivos oficiales ya están en disco.")
    else:
        titulo(f"Descargando {len(cola)} ZIP ({tam(sum(a['size'] for a in cola))})")
        TARGET_DIR.mkdir(parents=True, exist_ok=True)
        fallidos: list[tuple[str, str]] = []
        total = len(cola)
        for indice, archivo in enumerate(cola, start=1):
            etiqueta = f"[{indice}/{total}] {archivo['name']}"
            print(f"  {etiqueta}  {tam(archivo['size'])}")
            try:
                descargar_uno(archivo, TARGET_DIR, args.timeout, args.retries, etiqueta)
            except (RuntimeError, OSError) as exc:
                print(f"    ERROR: {exc}", file=sys.stderr)
                fallidos.append((archivo["name"], str(exc)))
        if fallidos:
            titulo(f"{len(fallidos)} archivos no se pudieron descargar")
            for ruta, motivo in fallidos:
                print(f"  {ruta} -> {motivo}")
            print("\n  Vuelva a ejecutar el script: reanudará el .part o lo que falte.")
            return 1

    titulo("Verificando los ZIP")
    ausentes, corruptos = verificar_zips(archivos, TARGET_DIR, True)
    if ausentes or corruptos:
        for ruta in ausentes:
            print(f"  FALTA:    {ruta}")
        for ruta, motivo in corruptos:
            print(f"  PROBLEMA: {ruta} -> {motivo}")
        return 1
    print("  MD5 de los ZIP coinciden con figshare.")

    titulo("Extrayendo ZIP (sin modificar el contenido de las imágenes)")
    for archivo in archivos:
        carpeta = extraer_zip(archivo, TARGET_DIR, args.force)
        print(f"  {archivo['name']} -> {carpeta.relative_to(REPO_ROOT).as_posix()}/")

    resumen = contar_imagenes(TARGET_DIR)
    titulo("Conteo local de imágenes (provisional)")
    print(f"  Encontradas: {resumen['total']}   Declaradas: {IMAGENES_DECLARADAS}")
    print(f"  train declarado: {TRAIN_DECLARADAS}   test declarado: {TEST_DECLARADAS}")
    for carpeta, n in resumen["por_carpeta"].items():
        print(f"    {carpeta}: {n}")
    print("  Este conteo no sustituye la validación de clases, anotaciones y corrupción.")
    print("  Actualice data/raw/indigo/README.md con las cantidades verificadas.")

    verificacion = {
        "tamano_zip": True,
        "md5_zip": True,
        "imagenes_encontradas": resumen["total"],
        "coincide_con_840": resumen["total"] == IMAGENES_DECLARADAS,
    }
    escribir_manifiesto(articulo, archivos, duplicados, resumen, verificacion)

    print("\n  Recuerde: este script no transforma imágenes y no entrena nada.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario. Los ZIP completos y los .part se conservan;")
        print("vuelva a ejecutar el script para reanudar.", file=sys.stderr)
        sys.exit(130)
