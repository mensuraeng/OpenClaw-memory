export interface OperationalAlert {
  id: string;
  categoria: "financeiro" | "licitacao" | "obra" | "sistema" | "comercial" | "agenda";
  severidade: "critico" | "atencao" | "info";
  empresa?: string;
  titulo: string;
  detalhe: string;
  prazoLabel?: string;
  origem?: string;
  acao?: string;
}

export interface AnalyticsInsight {
  empresa: string;
  sessoes: number;
  usuarios: number;
  novos: number;
  bouncePct: number;
  principalOrigem?: string;
  paginaTop?: string;
  leitura: string;
}

function parseMoney(raw?: string | null): number | null {
  if (!raw) return null;
  const cleaned = raw.replace(/[^\d,.-]/g, "").replace(/\.(?=\d{3}(\D|$))/g, "").replace(",", ".");
  const value = Number(cleaned);
  return Number.isFinite(value) ? value : null;
}

export function buildOperationalAlerts(): OperationalAlert[] {
  const alerts: OperationalAlert[] = [
    {
      id: "fin-irpj-csll-mia",
      categoria: "financeiro",
      severidade: "atencao",
      empresa: "MIA",
      titulo: "IRPJ e CSLL pendentes de apuração",
      detalhe: "Pagamento trimestral vence em 30/04 e ainda depende de apuração do valor.",
      prazoLabel: "30/04",
      origem: "contas_pagar_telegram.py",
      acao: "Apurar valor e travar agenda de pagamento.",
    },
    {
      id: "fin-gf-mia",
      categoria: "financeiro",
      severidade: "atencao",
      empresa: "MIA",
      titulo: "Boleto GF Condomínios no radar",
      detalhe: "Vence em 20/04 e pede conferência explícita de beneficiário antes de pagar.",
      prazoLabel: "20/04",
      origem: "contas_pagar_telegram.py",
      acao: "Validar beneficiário e valor real antes de autorizar baixa.",
    },
    {
      id: "lic-barretos-hoje",
      categoria: "licitacao",
      severidade: "critico",
      empresa: "PCS",
      titulo: "Licitação de Barretos vence hoje",
      detalhe: "Aviso de Contratação Direta nº 1283/2026/2026 com fechamento às 16:00.",
      prazoLabel: "Hoje 16:00",
      origem: "licitacoes_email.py",
      acao: "Decidir entrada imediata ou descartar para evitar corrida sem critério.",
    },
    {
      id: "obra-ccsp-rdo",
      categoria: "obra",
      severidade: "atencao",
      empresa: "MIA",
      titulo: "CCSP Casa 7 depende de disciplina de RDO",
      detalhe: "Fluxo de cobrança existe, mas houve falha recente no script e o RDO continua sendo ponto sensível do dia.",
      origem: "ccsp_rdo_cobranca.py",
      acao: "Confirmar recebimento real do RDO e estabilizar automação antes de confiar no fechamento.",
    },
    {
      id: "sistema-fallback",
      categoria: "sistema",
      severidade: "atencao",
      empresa: "GERAL",
      titulo: "Fallback de modelos ainda não está provado",
      detalhe: "Microtestes passaram, mas a cadeia real de fallback segue sem validação robusta.",
      origem: "MEMORY.md",
      acao: "Rodar teste forte com cenário real de degradação controlada.",
    },
  ];

  return alerts;
}

export function buildAnalyticsInsights(): AnalyticsInsight[] {
  const mensuraBounce = 58.3;
  const miaBounce = 64.1;

  return [
    {
      empresa: "MENSURA",
      sessoes: 412,
      usuarios: 287,
      novos: 198,
      bouncePct: mensuraBounce,
      principalOrigem: "Organic Search",
      paginaTop: "/",
      leitura: mensuraBounce > 55
        ? "Boa tração orgânica, mas ainda há vazamento alto na primeira visita."
        : "Aquisição saudável com retenção aceitável.",
    },
    {
      empresa: "MIA",
      sessoes: 156,
      usuarios: 121,
      novos: 98,
      bouncePct: miaBounce,
      principalOrigem: "Direct",
      paginaTop: "/",
      leitura: miaBounce > 60
        ? "Dependência de tráfego direto e conversão de primeira visita ainda fraca."
        : "Marca sustenta tráfego, mas ainda precisa ampliar descoberta.",
    },
  ];
}

export function summarizePayablesRisk() {
  const vivo1 = parseMoney("164,67");
  const vivo2 = parseMoney("35,48");
  const conhecido = [vivo1, vivo2].filter((v): v is number => v !== null).reduce((sum, v) => sum + v, 0);

  return {
    pendentes: 15,
    valorConhecido: conhecido,
    leitura: "Existe conta relevante misturada com ruído de classificação. A dor não é volume, é triagem ruim.",
  };
}
