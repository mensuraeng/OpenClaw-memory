#!/usr/bin/env python3
"""
Monitor de Licitações - PNCP (Portal Nacional de Contratações Públicas)
Busca licitações de Gerenciamento, Fiscalização e Manutenção de Obras em aberto.

Uso:
  python3 monitor_licitacoes.py              # Busca padrão, exibe no terminal
  python3 monitor_licitacoes.py --telegram   # Envia relatório via Telegram
  python3 monitor_licitacoes.py --dias 14    # Prazo mínimo de 14 dias
  python3 monitor_licitacoes.py --uf SP      # Filtrar por estado
"""

import json
import sys
import os
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

BRT = timezone(timedelta(hours=-3))

# Termos de busca — cada termo gera uma consulta separada
TERMOS_BUSCA = [
    "gerenciamento de obras",
    "gerenciamento obras",
    "supervisão de obras",
    "fiscalização de obras",
    "fiscalização obras",
    "manutenção predial",
    "manutenção de obras",
    "coordenação de obras",
]

# Palavras-chave obrigatórias no objeto (ao menos UMA deve estar presente)
PALAVRAS_RELEVANTES = [
    "gerenciamento", "gerenciamento de obra", "gerenciamento de obras",
    "fiscalização", "fiscalização de obra", "fiscalização de obras",
    "supervisão", "supervisão de obras",
    "manutenção predial", "manutenção de obra", "manutenção preventiva",
    "coordenação de obra", "coordenação de obras",
    "engenharia civil", "engenheiro civil",
    "controle de obra", "controle de obras",
    "acompanhamento de obra",
    "planejamento de obra",
]

# Palavras que descartam o resultado (falsos positivos)
PALAVRAS_EXCLUIR = [
    "mídias digitais", "redes sociais", "conferência", "congresso",
    "veículo", "aquisição de veículo", "equipamento hospitalar",
    "limpeza urbana", "varrição", "coleta de lixo",
    "merenda", "alimentação escolar", "gêneros alimentícios",
]

def e_relevante(descricao):
    """Verifica se o objeto da licitação é relevante para construção civil."""
    desc_lower = descricao.lower()
    # Descartar falsos positivos
    for p in PALAVRAS_EXCLUIR:
        if p.lower() in desc_lower:
            return False
    # Exigir pelo menos uma palavra relevante
    for p in PALAVRAS_RELEVANTES:
        if p.lower() in desc_lower:
            return True
    return False

PNCP_SEARCH = "https://pncp.gov.br/api/search/"
PNCP_BASE   = "https://pncp.gov.br"

def fetch_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except Exception as e:
        print(f"  [warn] Erro ao buscar {url}: {e}", file=sys.stderr)
        return {}

def search_licitacoes(termo, pagina=1, tam=50):
    params = urllib.parse.urlencode({
        "q": termo,
        "tipos_documento": "edital",
        "status": "recebendo_proposta",
        "pagina": pagina,
        "tam_pagina": tam,
    })
    url = f"{PNCP_SEARCH}?{params}"
    return fetch_json(url)

def parse_dt(s):
    """Converte string de data/hora para datetime BRT."""
    if not s:
        return None
    try:
        s_clean = s[:19]  # remove timezone suffix
        dt = datetime.fromisoformat(s_clean)
        return dt.replace(tzinfo=BRT)
    except Exception:
        return None

def format_dt(dt):
    if not dt:
        return "—"
    return dt.strftime("%d/%m/%Y %H:%M")

def format_valor(v):
    if v is None:
        return "—"
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(v)

def coletar_licitacoes(filtro_uf=None, dias_minimos=0):
    """Coleta e deduplica licitações de todos os termos."""
    vistos = set()
    licitacoes = []
    agora = datetime.now(BRT)

    for termo in TERMOS_BUSCA:
        data = search_licitacoes(termo)
        items = data.get("items", [])
        for item in items:
            uid = item.get("id", "")
            if uid in vistos:
                continue
            vistos.add(uid)

            # Filtro de relevância (objeto deve ser de construção civil)
            descricao = item.get("description", "")
            if not e_relevante(descricao):
                continue

            # Filtro por UF
            if filtro_uf and item.get("uf", "").upper() != filtro_uf.upper():
                continue

            # Prazo de encerramento
            prazo = parse_dt(item.get("data_fim_vigencia", ""))
            if prazo and prazo < agora:
                continue  # já encerrado

            # Filtro de dias mínimos restantes
            if dias_minimos > 0 and prazo:
                dias_restantes = (prazo - agora).days
                if dias_restantes < dias_minimos:
                    continue

            valor_raw = item.get("valor_global")
            licitacoes.append({
                "titulo":     item.get("title", "—"),
                "descricao":  item.get("description", "—"),
                "orgao":      item.get("orgao_nome", "—"),
                "unidade":    item.get("unidade_nome", ""),
                "municipio":  item.get("municipio_nome", "—"),
                "uf":         item.get("uf", "—").upper(),
                "modalidade": item.get("modalidade_licitacao_nome", "—"),
                "valor":      format_valor(valor_raw),
                "prazo":      prazo,
                "publicado":  parse_dt(item.get("data_publicacao_pncp", "")),
                "numero_pncp": item.get("numero_controle_pncp", "—"),
                "url":        PNCP_BASE + item.get("item_url", ""),
                "situacao":   item.get("situacao_nome", "—"),
                "cancelado":  item.get("cancelado", False),
            })

    # Ordena: SP primeiro, depois demais UFs alfabético; dentro de cada UF por prazo
    def sort_key(x):
        uf = x.get("uf", "ZZ")
        uf_order = "AA" if uf == "SP" else uf
        prazo = x["prazo"] or datetime.max.replace(tzinfo=BRT)
        return (uf_order, prazo)

    licitacoes.sort(key=sort_key)
    return licitacoes

def dias_restantes_str(prazo):
    if not prazo:
        return "prazo indefinido"
    agora = datetime.now(BRT)
    delta = (prazo - agora).days
    if delta < 0:
        return "ENCERRADO"
    elif delta == 0:
        return "⚠️ HOJE"
    elif delta == 1:
        return "⚠️ AMANHÃ"
    elif delta <= 5:
        return f"⚠️ {delta} dias"
    else:
        return f"{delta} dias"

def formatar_relatorio_texto(licitacoes, filtro_uf=None):
    agora = datetime.now(BRT)
    linhas = []
    linhas.append("=" * 60)
    linhas.append("📋 RELATÓRIO DE LICITAÇÕES — CONSTRUÇÃO CIVIL")
    linhas.append(f"   Gerenciamento | Fiscalização | Manutenção de Obras")
    linhas.append(f"   Gerado em: {agora.strftime('%d/%m/%Y %H:%M')} BRT")
    if filtro_uf:
        linhas.append(f"   Filtro UF: {filtro_uf}")
    linhas.append(f"   Total encontrado: {len(licitacoes)} licitações")
    linhas.append("=" * 60)

    if not licitacoes:
        linhas.append("\nNenhuma licitação em aberto encontrada.")
        return "\n".join(linhas)

    uf_atual = None
    contador = 0
    for lic in licitacoes:
        contador += 1
        # Cabeçalho por estado
        if lic["uf"] != uf_atual:
            uf_atual = lic["uf"]
            linhas.append(f"\n{'═'*60}")
            linhas.append(f"  📍 ESTADO: {uf_atual}")
            linhas.append(f"{'═'*60}")

        prazo_str = format_dt(lic["prazo"])
        restante = dias_restantes_str(lic["prazo"])
        linhas.append(f"\n{'─'*60}")
        linhas.append(f"#{contador} {lic['titulo']}")
        linhas.append(f"   Órgão:      {lic['orgao']}")
        if lic["unidade"] and lic["unidade"] != lic["orgao"]:
            linhas.append(f"   Unidade:    {lic['unidade']}")
        linhas.append(f"   Local:      {lic['municipio']} / {lic['uf']}")
        linhas.append(f"   Modalidade: {lic['modalidade']}")
        linhas.append(f"   Valor:      {lic['valor']}")
        linhas.append(f"   Prazo:      {prazo_str} ({restante})")
        linhas.append(f"   PNCP:       {lic['numero_pncp']}")
        linhas.append(f"   Objeto:     {lic['descricao'][:200]}{'...' if len(lic['descricao']) > 200 else ''}")
        linhas.append(f"   🔗 {lic['url']}")

    linhas.append(f"\n{'='*60}")
    linhas.append("Fonte: PNCP — pncp.gov.br")
    return "\n".join(linhas)

def formatar_relatorio_telegram(licitacoes, filtro_uf=None):
    """Formata para Telegram com Markdown."""
    agora = datetime.now(BRT)
    partes = []
    partes.append(f"📋 *LICITAÇÕES — CONSTRUÇÃO CIVIL*")
    partes.append(f"_Gerenciamento | Fiscalização | Manutenção_")
    partes.append(f"_{agora.strftime('%d/%m/%Y %H:%M')} BRT — {len(licitacoes)} encontradas_\n")

    if not licitacoes:
        partes.append("Nenhuma licitação em aberto encontrada.")
        return "\n".join(partes)

    for i, lic in enumerate(licitacoes, 1):
        restante = dias_restantes_str(lic["prazo"])
        prazo_str = format_dt(lic["prazo"])
        bloco = []
        bloco.append(f"*#{i} {lic['titulo']}*")
        bloco.append(f"🏛 {lic['orgao']}")
        bloco.append(f"📍 {lic['municipio']}/{lic['uf']} | {lic['modalidade']}")
        bloco.append(f"💰 {lic['valor']}")
        bloco.append(f"⏰ {prazo_str} \\({restante}\\)")
        bloco.append(f"📄 `{lic['numero_pncp']}`")
        obj = lic['descricao'][:180] + ("..." if len(lic['descricao']) > 180 else "")
        bloco.append(f"_{obj}_")
        bloco.append(f"[Ver edital]({lic['url']})")
        partes.append("\n".join(bloco))

    partes.append(f"\n_Fonte: PNCP — pncp.gov.br_")
    # Telegram tem limite de 4096 chars por mensagem — dividir se necessário
    return "\n\n".join(partes)

def enviar_telegram(texto):
    """Envia via OpenClaw CLI (já configurado)."""
    import subprocess
    # Divide em blocos de até 4000 chars (margem de segurança)
    blocos = []
    while len(texto) > 4000:
        corte = texto.rfind("\n\n", 0, 4000)
        if corte == -1:
            corte = 4000
        blocos.append(texto[:corte])
        texto = texto[corte:].strip()
    blocos.append(texto)

    for bloco in blocos:
        resultado = subprocess.run(
            ["openclaw", "msg", "send", "--channel", "telegram", "--message", bloco],
            capture_output=True, text=True
        )
        if resultado.returncode != 0:
            print(f"Erro ao enviar Telegram: {resultado.stderr}", file=sys.stderr)

def buscar_valor_detalhe(lic):
    """Busca valor estimado via API de detalhe do edital."""
    pncp = lic.get("numero_pncp", "")
    # Formato: CNPJ-1-SEQUENCIAL/ANO
    try:
        partes = pncp.split("-")
        cnpj = partes[0]
        seq_ano = partes[2]  # ex: 000534/2026
        seq, ano = seq_ano.split("/")
        seq_int = int(seq)
        url = f"https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq_int}"
        det = fetch_json(url)
        v = det.get("valorTotalEstimado") or det.get("valorTotalHomologado")
        if v is not None:
            lic["valor"] = format_valor(v)
    except Exception:
        pass
    return lic

def enriquecer_valores(licitacoes, workers=10):
    """Busca valores em paralelo para licitações sem valor informado."""
    sem_valor = [l for l in licitacoes if l["valor"] == "—"]
    if not sem_valor:
        return licitacoes
    print(f"  Buscando valores para {len(sem_valor)} editais...", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(buscar_valor_detalhe, l): l for l in sem_valor}
        for f in as_completed(futures):
            f.result()  # atualiza in-place
    return licitacoes

def salvar_json(licitacoes, caminho):
    """Salva resultado em JSON para integração futura."""
    dados = []
    for lic in licitacoes:
        d = dict(lic)
        d["prazo"] = lic["prazo"].isoformat() if lic["prazo"] else None
        d["publicado"] = lic["publicado"].isoformat() if lic["publicado"] else None
        dados.append(d)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"✅ Salvo em {caminho}")

def main():
    p = argparse.ArgumentParser(description="Monitor de Licitações PNCP — Construção Civil")
    p.add_argument("--uf",       default="", help="Filtrar por UF (ex: SP, RJ, MG)")
    p.add_argument("--dias",     type=int, default=0, help="Prazo mínimo em dias (0 = sem filtro)")
    p.add_argument("--telegram", action="store_true", help="Enviar relatório via Telegram")
    p.add_argument("--json",     default="", help="Salvar resultado em arquivo JSON")
    p.add_argument("--max",      type=int, default=999, help="Número máximo de licitações no relatório")
    p.add_argument("--valores",  action="store_true", help="Buscar valores estimados via API de detalhe (mais lento)")
    args = p.parse_args()

    print(f"🔍 Buscando licitações no PNCP...", file=sys.stderr)
    licitacoes = coletar_licitacoes(
        filtro_uf=args.uf or None,
        dias_minimos=args.dias,
    )

    # Limitar quantidade se pedido
    licitacoes = licitacoes[:args.max]

    # Enriquecer valores se solicitado
    if args.valores:
        licitacoes = enriquecer_valores(licitacoes)

    if args.json:
        salvar_json(licitacoes, args.json)

    if args.telegram:
        relatorio = formatar_relatorio_telegram(licitacoes, args.uf or None)
        enviar_telegram(relatorio)
        print(f"✅ Relatório enviado ao Telegram ({len(licitacoes)} licitações)", file=sys.stderr)
    else:
        print(formatar_relatorio_texto(licitacoes, args.uf or None))

if __name__ == "__main__":
    main()
