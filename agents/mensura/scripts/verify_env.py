#!/usr/bin/env python3
"""
verify_env.py — Verifica se o ambiente esta correto para o pipeline .mpp
Uso: python3 verify_env.py
Retorno: exit 0 se tudo OK, exit 1 se algum problema encontrado
"""
import sys
import subprocess
import importlib.metadata
import os

REQUIRED_MPXJ   = (16, 1, 0)
REQUIRED_JPYPE  = (1, 7, 0)
REQUIRED_JAVA   = 21
REQUIRED_PYTHON = (3, 10)

errors   = []
warnings = []
ok       = []

# 1. Python version
pv = sys.version_info
if pv >= REQUIRED_PYTHON:
    ok.append(f"Python {pv.major}.{pv.minor}.{pv.micro}")
else:
    errors.append(f"Python {pv.major}.{pv.minor} < {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]} requerido")

# 2. mpxj version
try:
    mpxj_ver = importlib.metadata.version("mpxj")
    parts = tuple(int(x) for x in mpxj_ver.split(".")[:3])
    if parts == REQUIRED_MPXJ:
        ok.append(f"mpxj {mpxj_ver} (versao fixada correta)")
    elif parts > REQUIRED_MPXJ:
        warnings.append(f"mpxj {mpxj_ver} > {'.'.join(map(str,REQUIRED_MPXJ))} — API pode ter mudado, teste antes de usar")
    else:
        errors.append(f"mpxj {mpxj_ver} < {'.'.join(map(str,REQUIRED_MPXJ))} — atualize: pip install mpxj==16.1.0 --break-system-packages")
except Exception as e:
    errors.append(f"mpxj nao instalado: {e}")

# 3. JPype1 version
try:
    jpype_ver = importlib.metadata.version("JPype1")
    parts = tuple(int(x) for x in jpype_ver.split(".")[:3])
    if parts >= REQUIRED_JPYPE:
        ok.append(f"JPype1 {jpype_ver}")
    else:
        warnings.append(f"JPype1 {jpype_ver} < {'.'.join(map(str,REQUIRED_JPYPE))} — pode ter incompatibilidades")
except Exception as e:
    errors.append(f"JPype1 nao instalado: {e}")

# 4. Java version
try:
    result = subprocess.run(["java", "-version"], capture_output=True, text=True)
    output = result.stderr or result.stdout
    import re
    match = re.search(r'version "(\d+)', output)
    if match:
        java_major = int(match.group(1))
        if java_major >= REQUIRED_JAVA:
            ok.append(f"Java {java_major} (OpenJDK detectado)")
        else:
            errors.append(f"Java {java_major} < {REQUIRED_JAVA} requerido — instale: apt-get install default-jre")
    else:
        errors.append("Java nao encontrado ou versao nao detectada")
except FileNotFoundError:
    errors.append("Java nao encontrado no PATH — instale: apt-get install default-jre")

# 5. API org.mpxj funcional (teste real com JVM)
try:
    import mpxj
    import jpype
    import jpype.imports
    if not jpype.isJVMStarted():
        jpype.startJVM()
    from org.mpxj.reader import UniversalProjectReader
    from org.mpxj import ProjectFile
    ok.append("API org.mpxj carregada e funcional (JVM iniciada, classes acessiveis)")
except Exception as e:
    errors.append(f"API org.mpxj FALHOU: {e}")

# 6. Diretorios de memoria
dirs = [
    "/root/.openclaw/workspace/agents/mensura/scripts",
    "/root/.openclaw/workspace/memory/obras",
]
for d in dirs:
    if os.path.isdir(d):
        ok.append(f"Diretorio existe: {d}")
    else:
        errors.append(f"Diretorio ausente: {d} — crie com: mkdir -p {d}")

# --- Relatorio final ---
print()
print("=" * 60)
print("  VERIFICACAO DE AMBIENTE — Pipeline MPP -> Relatorio")
print("=" * 60)
for msg in ok:
    print(f"  [OK]   {msg}")
for msg in warnings:
    print(f"  [WARN] {msg}")
for msg in errors:
    print(f"  [ERRO] {msg}")
print("=" * 60)
if errors:
    print(f"  RESULTADO: {len(errors)} ERRO(S) encontrado(s). Corrija antes de usar.")
    print()
    sys.exit(1)
elif warnings:
    print(f"  RESULTADO: OK com {len(warnings)} aviso(s). Ambiente funcional.")
else:
    print("  RESULTADO: TUDO OK — ambiente 100% validado.")
print()
