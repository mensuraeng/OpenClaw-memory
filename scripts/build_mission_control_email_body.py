from pathlib import Path

base = Path('/root/.openclaw/workspace/exports')
out = base / 'mission-control-email-body.txt'
parts = [
    ('prd-mission-control-openclaw.txt', 'PRD'),
    ('mission-control-v1-design.txt', 'DESIGN V1'),
    ('mission-control-v1-implementation-plan.txt', 'IMPLEMENTATION PLAN'),
    ('mission-control-patch-list-v1.txt', 'PATCH LIST V1'),
]

with out.open('w', encoding='utf-8') as f:
    f.write("Alê,\n\n")
    f.write("Segue abaixo o material do Mission Control em texto puro para visualização e revisão no Claude.\n\n")
    f.write("Arquivos incluídos nesta entrega:\n")
    for name, _ in parts:
        f.write(f"- {name}\n")
    f.write("\nSe quiser, no próximo passo eu também consolido tudo em um único arquivo mestre com índice melhor.\n\n")
    f.write("Flávia\n")
    for name, title in parts:
        p = base / name
        f.write(f"\n\n{title}\n")
        f.write("=" * 50 + "\n\n")
        f.write(p.read_text(encoding='utf-8'))
        f.write("\n")

print(out)
print(out.stat().st_size)
