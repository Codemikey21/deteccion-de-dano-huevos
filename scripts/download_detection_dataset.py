#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Descarga el conjunto Egg-Detection desde Hugging Face a data/raw/detection/.

Conjunto: afshin-dini/Egg-Detection
Licencia: MIT (verificada el 21/09/2026 contra la API de Hugging Face)
Uso: detección de huevos (clase única `egg` tras fusionar las clases originales,
     cuyos nombres exactos están pendientes de leer en data/data.yaml).

Este script SOLO descarga. Deliberadamente NO hace nada de lo siguiente:
  - no transforma, redimensiona ni convierte imágenes;
  - no divide en train/validation/test (respeta la estructura original);
  - no reetiqueta ni fusiona clases;
  - no entrena nada;
  - no borra archivos.

No requiere dependencias externas: usa solo la biblioteca estándar de Python.

Uso:
    python scripts/download_detection_dataset.py --dry-run     # consultar sin descargar
    python scripts/download_detection_dataset.py               # descargar lo que falte
    python scripts/download_detection_dataset.py --verify-only # comprobar lo ya descargado
    python scripts/download_detection_dataset.py --force       # re-descargar todo

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
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ID = "afshin-dini/Egg-Detection"
DEFAULT_REVISION = "main"
LICENSE = "MIT"

TREE_URL = "https://huggingface.co/api/datasets/{repo}/tree/{rev}?recursive=true"
RESOLVE_URL = "https://huggingface.co/datasets/{repo}/resolve/{rev}/{path}"

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_DIR = REPO_ROOT / "data" / "raw" / "detection"
MANIFEST_PATH = TARGET_DIR / "_manifest.json"

USER_AGENT = "deteccion-huevos-uab/0.1 (proyecto academico; urllib)"
CHUNK = 1 << 20  # 1 MiB

# El conjunto trae su propio README.md en la raíz, que colisionaría con el README de
# documentación de la carpeta. Se guarda con otro nombre para conservar ambos.
RENOMBRADOS = {
    "README.md": "_origen_README.md",
}

EXTENSIONES_IMAGEN = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


# Códigos HTTP que justifican reintentar. El resto (404, 401, 403) son definitivos.
RETRYABLE_HTTP = {408, 425, 429, 500, 502, 503, 504}


def es_imagen(ruta: str) -> bool:
    return Path(ruta).suffix.lower() in EXTENSIONES_IMAGEN


def hasher_git_blob(tamano: int) -> "hashlib._Hash":
    """Inicia el SHA-1 de un blob Git: sha1(b'blob <n>\\0' + contenido)."""
    h = hashlib.sha1()
    h.update(f"blob {tamano}".encode("ascii"))
    h.update(b"\0")
    return h


def git_blob_sha1_archivo(ruta: Path, tamano: int) -> str:
    h = hasher_git_blob(tamano)
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(CHUNK), b""):
            h.update(bloque)
    return h.hexdigest()


def configurar_salida() -> None:
    """Fuerza UTF-8 en la consola para que los acentos no rompan la ejecución."""
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


# --------------------------------------------------------------------------
# Red
# --------------------------------------------------------------------------

def abrir(url: str, timeout: int):
    peticion = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(peticion, timeout=timeout)


def con_reintentos(accion, descripcion: str, reintentos: int):
    """Ejecuta `accion` reintentando solo ante fallos de red o HTTP transitorios.

    No captura OSError genérico: un disco lleno, un permiso denegado o cualquier
    error de sistema de archivos debe abortar de inmediato, no reintentarse.
    """
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

    raise RuntimeError(f"{descripcion}: agotados {reintentos} intentos. Último error: {ultimo_error}")


def listar_archivos(repo: str, revision: str, timeout: int,
                    reintentos: int) -> tuple[list[dict], str | None]:
    """Consulta el árbol del repositorio.

    Devuelve (archivos, commit). El commit es el valor de la cabecera
    `X-Repo-Commit` si Hugging Face lo envía; si no, None. No se inventa.
    """
    url = TREE_URL.format(repo=urllib.parse.quote(repo), rev=urllib.parse.quote(revision))

    def _pedir():
        with abrir(url, timeout) as respuesta:
            commit = respuesta.headers.get("X-Repo-Commit") or respuesta.headers.get("x-repo-commit")
            if commit:
                commit = commit.strip() or None
            cuerpo = json.loads(respuesta.read().decode("utf-8"))
            return cuerpo, commit

    arbol, commit = con_reintentos(_pedir, "Consulta del listado de archivos", reintentos)

    archivos = []
    for entrada in arbol:
        if entrada.get("type") != "file":
            continue
        lfs = entrada.get("lfs") or {}
        ruta = entrada["path"]
        sha256_lfs = lfs.get("oid")
        archivos.append({
            "path": ruta,
            "local": RENOMBRADOS.get(ruta, ruta),
            "size": int(entrada.get("size", 0)),
            # LFS: sha256 real del contenido. Git normal: oid SHA-1 del blob.
            "sha256": sha256_lfs,
            "git_oid": None if sha256_lfs else entrada.get("oid"),
        })
    archivos.sort(key=lambda a: a["path"])
    return archivos, commit


# --------------------------------------------------------------------------
# Disco
# --------------------------------------------------------------------------

def sha256_local(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(CHUNK), b""):
            h.update(bloque)
    return h.hexdigest()


def clasificar(archivos: list[dict], destino: Path) -> tuple[list, list, list]:
    """Separa los archivos en: faltantes, ya presentes y en conflicto.

    Un archivo está "en conflicto" si existe en disco con un tamaño distinto al del
    origen. No se sobrescribe: se informa y se deja intacto salvo que se use --force.
    """
    faltantes, presentes, conflictos = [], [], []
    for archivo in archivos:
        local = destino / archivo["local"]
        if not local.exists():
            faltantes.append(archivo)
        elif local.stat().st_size == archivo["size"]:
            presentes.append(archivo)
        else:
            conflictos.append((archivo, local.stat().st_size))
    return faltantes, presentes, conflictos


def descargar_uno(repo: str, revision: str, archivo: dict, destino: Path,
                  timeout: int, reintentos: int, etiqueta: str) -> None:
    """Descarga un archivo a un temporal .part y solo entonces lo renombra.

    Escribir primero en .part evita que una descarga interrumpida deje un archivo
    incompleto con aspecto de válido, que es lo que rompería una segunda ejecución.
    """
    url = RESOLVE_URL.format(
        repo=urllib.parse.quote(repo),
        rev=urllib.parse.quote(revision),
        path=urllib.parse.quote(archivo["path"]),
    )
    final = destino / archivo["local"]
    parcial = final.with_name(final.name + ".part")
    final.parent.mkdir(parents=True, exist_ok=True)

    def _bajar():
        descargados = 0
        h256 = hashlib.sha256()
        hgit = hasher_git_blob(archivo["size"]) if archivo.get("git_oid") else None
        with abrir(url, timeout) as respuesta, parcial.open("wb") as salida:
            total = int(respuesta.headers.get("Content-Length") or archivo["size"])
            while True:
                bloque = respuesta.read(CHUNK)
                if not bloque:
                    break
                salida.write(bloque)
                h256.update(bloque)
                if hgit is not None:
                    hgit.update(bloque)
                descargados += len(bloque)
                if total > CHUNK:
                    barra(etiqueta, descargados, total)
        if total > CHUNK:
            sys.stdout.write("\r" + " " * 96 + "\r")
            sys.stdout.flush()
        return descargados, h256.hexdigest(), (hgit.hexdigest() if hgit else None)

    try:
        descargados, digest256, digest_git = con_reintentos(
            _bajar, f"Descarga de {archivo['path']}", reintentos
        )

        if archivo["size"] and descargados != archivo["size"]:
            raise RuntimeError(
                f"tamaño incorrecto: se esperaban {archivo['size']} bytes y llegaron {descargados}"
            )
        if archivo["sha256"] and digest256 != archivo["sha256"]:
            raise RuntimeError("el sha256 del archivo descargado no coincide con el del origen")
        if archivo.get("git_oid") and digest_git != archivo["git_oid"]:
            raise RuntimeError("el oid Git del archivo descargado no coincide con el del origen")

        parcial.replace(final)
    except Exception:
        parcial.unlink(missing_ok=True)
        raise


# --------------------------------------------------------------------------
# Verificación y resumen
# --------------------------------------------------------------------------

def verificar(archivos: list[dict], destino: Path, comprobar_hash: bool) -> tuple[list, list]:
    ausentes, corruptos = [], []
    total = len(archivos)
    for indice, archivo in enumerate(archivos, start=1):
        local = destino / archivo["local"]
        if not local.exists():
            ausentes.append(archivo["local"])
            continue
        if local.stat().st_size != archivo["size"]:
            corruptos.append((archivo["local"], "tamaño distinto al del origen"))
            continue
        if comprobar_hash and archivo["sha256"]:
            barra(f"hash [{indice}/{total}]", indice, total)
            if sha256_local(local) != archivo["sha256"]:
                corruptos.append((archivo["local"], "sha256 distinto al del origen"))
                continue
        if comprobar_hash and archivo.get("git_oid"):
            barra(f"hash [{indice}/{total}]", indice, total)
            if git_blob_sha1_archivo(local, archivo["size"]) != archivo["git_oid"]:
                corruptos.append((archivo["local"], "oid Git distinto al del origen"))
    if comprobar_hash:
        sys.stdout.write("\r" + " " * 96 + "\r")
        sys.stdout.flush()
    return ausentes, corruptos


def resumir_contenido(destino: Path) -> dict:
    """Cuenta lo que hay realmente en disco, sin suponer nada."""
    if not destino.exists():
        return {"total": 0, "imagenes": 0, "bytes": 0, "por_extension": {}, "por_carpeta": {}}

    por_extension: dict[str, int] = {}
    por_carpeta: dict[str, int] = {}
    total = 0
    total_bytes = 0

    for ruta in sorted(destino.rglob("*")):
        if not ruta.is_file() or ruta.name.endswith(".part") or ruta.name == MANIFEST_PATH.name:
            continue
        # El README de la carpeta es documentación nuestra, no material del conjunto.
        if ruta.parent == destino and ruta.name == "README.md":
            continue
        total += 1
        total_bytes += ruta.stat().st_size
        ext = ruta.suffix.lower() or "(sin extensión)"
        por_extension[ext] = por_extension.get(ext, 0) + 1
        carpeta = ruta.parent.relative_to(destino).as_posix() or "."
        por_carpeta[carpeta] = por_carpeta.get(carpeta, 0) + 1

    return {
        "total": total,
        "imagenes": por_extension.get(".jpg", 0) + por_extension.get(".jpeg", 0)
                    + por_extension.get(".png", 0),
        "bytes": total_bytes,
        "por_extension": dict(sorted(por_extension.items())),
        "por_carpeta": dict(sorted(por_carpeta.items())),
    }


def imprimir_resumen(resumen: dict) -> None:
    titulo("Contenido verificado en disco")
    print(f"  Archivos: {resumen['total']}")
    if resumen.get("imagenes") is not None:
        print(f"  Imágenes: {resumen['imagenes']}")
    print(f"  Tamaño:   {tam(resumen['bytes'])}")
    if resumen["por_extension"]:
        print("  Por extensión:")
        for ext, n in resumen["por_extension"].items():
            print(f"    {ext:<20} {n:>5}")
    if resumen["por_carpeta"]:
        print("  Por carpeta:")
        for carpeta, n in resumen["por_carpeta"].items():
            print(f"    {carpeta:<40} {n:>5}")


def escribir_manifiesto(archivos: list[dict], revision: str, commit: str | None,
                        resumen: dict, verificacion: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    n_imagenes = sum(1 for a in archivos if es_imagen(a["path"]))
    contenido = {
        "dataset": REPO_ID,
        "url": f"https://huggingface.co/datasets/{REPO_ID}",
        "licencia": LICENSE,
        "revision_solicitada": revision,
        "commit_real": commit,
        "descargado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "archivos": len(archivos),
        "imagenes": n_imagenes,
        "bytes_totales": sum(a["size"] for a in archivos),
        "verificacion": verificacion,
        "resumen_local": resumen,
        "detalle_archivos": archivos,
    }
    MANIFEST_PATH.write_text(
        json.dumps(contenido, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\n  Manifiesto escrito en {MANIFEST_PATH.relative_to(REPO_ROOT)}")
    if commit:
        print(f"  Commit real: {commit}")
    else:
        print("  Commit real: no disponible (Hugging Face no envió X-Repo-Commit)")


# --------------------------------------------------------------------------
# Programa principal
# --------------------------------------------------------------------------

def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Descarga el conjunto Egg-Detection (Hugging Face, licencia MIT) "
                    "a data/raw/detection/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="consulta el listado y muestra qué se descargaría, sin escribir nada")
    parser.add_argument("--verify-only", action="store_true",
                        help="verifica lo ya descargado y termina, sin descargar")
    parser.add_argument("--force", action="store_true",
                        help="re-descarga y sobrescribe archivos existentes")
    parser.add_argument("--check-hash", action="store_true",
                        help="al verificar, recalcula SHA-256 (LFS) y SHA-1 blob Git")
    parser.add_argument("--revision", default=DEFAULT_REVISION,
                        help=f"revisión del repositorio (por defecto: {DEFAULT_REVISION})")
    parser.add_argument("--timeout", type=int, default=60,
                        help="tiempo máximo de espera por petición, en segundos")
    parser.add_argument("--retries", type=int, default=4,
                        help="número total de intentos ante fallos de red")
    return parser


def main() -> int:
    configurar_salida()
    args = construir_parser().parse_args()

    print("=" * 78)
    print(f"  Conjunto: {REPO_ID}")
    print(f"  Licencia: {LICENSE}")
    print(f"  Destino:  {TARGET_DIR.relative_to(REPO_ROOT).as_posix()}/")
    print(f"  Revisión: {args.revision}")
    print("=" * 78)

    titulo("Consultando el listado de archivos del origen")
    try:
        archivos, commit = listar_archivos(REPO_ID, args.revision, args.timeout, args.retries)
    except RuntimeError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        print("Revise su conexión a internet y vuelva a intentarlo.", file=sys.stderr)
        return 1

    if not archivos:
        print("\nERROR: el origen no devolvió ningún archivo.", file=sys.stderr)
        return 1

    if commit:
        print(f"  Commit real:           {commit}")
    else:
        print("  Commit real:           no disponible (cabecera X-Repo-Commit ausente)")

    bytes_totales = sum(a["size"] for a in archivos)
    n_imagenes = sum(1 for a in archivos if es_imagen(a["path"]))
    print(f"  Archivos en el origen: {len(archivos)}")
    print(f"  Imágenes:              {n_imagenes}")
    print(f"  Tamaño total:          {tam(bytes_totales)}")

    faltantes, presentes, conflictos = clasificar(archivos, TARGET_DIR)

    titulo("Estado local")
    print(f"  Ya presentes y correctos: {len(presentes)}")
    print(f"  Por descargar:            {len(faltantes)}")
    print(f"  En conflicto:             {len(conflictos)}")

    if conflictos:
        print("\n  Estos archivos existen en disco con un tamaño distinto al del origen.")
        print("  NO se sobrescriben. Revíselos y, si desea reemplazarlos, use --force:")
        for archivo, tamano_local in conflictos[:20]:
            print(f"    {archivo['local']}  (local {tam(tamano_local)}, "
                  f"origen {tam(archivo['size'])})")
        if len(conflictos) > 20:
            print(f"    ... y {len(conflictos) - 20} más")

    # --- Solo verificar -----------------------------------------------------
    if args.verify_only:
        titulo("Verificación")
        ausentes, corruptos = verificar(archivos, TARGET_DIR, args.check_hash)
        if not ausentes and not corruptos:
            print("  Correcto: todos los archivos esperados están presentes y son consistentes.")
            imprimir_resumen(resumir_contenido(TARGET_DIR))
            return 0
        for ruta in ausentes:
            print(f"  FALTA:    {ruta}")
        for ruta, motivo in corruptos:
            print(f"  PROBLEMA: {ruta} -> {motivo}")
        print("\n  Ejecute el script sin --verify-only para completar la descarga.")
        return 1

    # --- Simulación ---------------------------------------------------------
    if args.dry_run:
        titulo("Simulación (--dry-run): no se ha escrito nada")
        pendientes = archivos if args.force else faltantes
        print(f"  Se descargarían {len(pendientes)} archivos")
        print(f"  Espacio necesario: {tam(sum(a['size'] for a in pendientes))}")
        print(f"  Espacio total del conjunto completo: {tam(bytes_totales)}")
        for archivo in pendientes[:10]:
            print(f"    {archivo['path']:<45} {tam(archivo['size'])}")
        if len(pendientes) > 10:
            print(f"    ... y {len(pendientes) - 10} más")
        return 2 if conflictos and not args.force else 0

    # --- Descarga -----------------------------------------------------------
    cola = archivos if args.force else faltantes
    if not cola:
        print("\n  No hay nada que descargar: el conjunto ya está completo.")
    else:
        titulo(f"Descargando {len(cola)} archivos ({tam(sum(a['size'] for a in cola))})")
        TARGET_DIR.mkdir(parents=True, exist_ok=True)
        fallidos: list[tuple[str, str]] = []
        total = len(cola)
        for indice, archivo in enumerate(cola, start=1):
            etiqueta = f"[{indice:>3}/{total}]"
            renombrado = "" if archivo["local"] == archivo["path"] else f"  -> {archivo['local']}"
            print(f"  {etiqueta} {archivo['path']:<45} {tam(archivo['size'])}{renombrado}")
            try:
                descargar_uno(REPO_ID, args.revision, archivo, TARGET_DIR,
                              args.timeout, args.retries, etiqueta)
            except (RuntimeError, OSError) as exc:
                print(f"    ERROR: {exc}", file=sys.stderr)
                fallidos.append((archivo["path"], str(exc)))

        if fallidos:
            titulo(f"{len(fallidos)} archivos no se pudieron descargar")
            for ruta, motivo in fallidos:
                print(f"  {ruta} -> {motivo}")
            print("\n  Vuelva a ejecutar el script: reanudará solo lo que falta.")
            return 1

    # --- Verificación final -------------------------------------------------
    titulo("Verificando la descarga")
    ausentes, corruptos = verificar(archivos, TARGET_DIR, args.check_hash)
    if ausentes or corruptos:
        for ruta in ausentes:
            print(f"  FALTA:    {ruta}")
        for ruta, motivo in corruptos:
            print(f"  PROBLEMA: {ruta} -> {motivo}")
        print("\n  La descarga NO está completa. Vuelva a ejecutar el script.")
        return 1

    print(f"  Correcto: los {len(archivos)} archivos esperados están presentes y son consistentes.")

    resumen = resumir_contenido(TARGET_DIR)
    imprimir_resumen(resumen)
    verificacion = {
        "tamano": True,
        "sha256_lfs_en_descarga": True,
        "git_oid_en_descarga": True,
        "hashes_recalculados_al_final": bool(args.check_hash),
        "ausentes": 0,
        "corruptos": 0,
    }
    escribir_manifiesto(archivos, args.revision, commit, resumen, verificacion)

    print("\n  Recuerde: este script no transforma imágenes, no divide particiones")
    print("  y no entrena nada. El material queda tal como está en el origen.")
    print("  Actualice data/raw/detection/README.md con las cantidades verificadas.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario. Los archivos ya completos se conservan;")
        print("vuelva a ejecutar el script para reanudar.", file=sys.stderr)
        sys.exit(130)
