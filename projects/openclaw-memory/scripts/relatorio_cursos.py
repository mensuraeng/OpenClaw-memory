#!/usr/bin/env python3
"""
Relatório semanal de cursos - Construção Civil
Roda toda sexta-feira às 16h (Brasília)
"""

import subprocess
import sys
import json
from datetime import datetime

PROMPT = """Você é um analista sênior de inteligência educacional e desenvolvimento profissional, especializado no setor da Construção Civil no Brasil.

Realize uma varredura criteriosa na internet para identificar cursos, treinamentos, certificações, workshops, MBAs, extensões, imersões e eventos educacionais para um profissional com o seguinte perfil:

PERFIL: Engenheiro civil / gerente de obras com foco em gerenciamento, planejamento e controle, coordenação e execução de obras, produtividade, gestão técnica e executiva, inovação aplicada à construção.

TEMAS PRIORITÁRIOS: Gerenciamento de obras, Lean Construction, Last Planner System, BIM, Planejamento e controle de cronogramas, Orçamentação e custos, Retrofit, Power BI e gestão por dados, Licitações e contratos, Liderança e gestão de equipes, Normas técnicas, Segurança do trabalho, Inovação e tecnologia na construção civil.

FONTES: SindusCon-SP, CREA-SP, CONFEA, CBIC, SENAI, SEBRAE, universidades reconhecidas, institutos técnicos setoriais.

FILTROS: Brasil (prioridade), online ou híbrido (preferência), presencial apenas se muito relevante (SP/Sudeste), inscrições abertas ou turma próxima. Evitar cursos genéricos, rasos ou de instituições pouco confiáveis.

Para cada curso selecionado, apresente:
1. Nome do curso
2. Instituição
3. Categoria (técnico, executivo, certificação, MBA, workshop, extensão, imersão)
4. Tema principal
5. Formato (online, presencial, híbrido)
6. Localidade (se aplicável)
7. Carga horária (se disponível)
8. Preço (se disponível)
9. Data/prazo de inscrição
10. Link oficial
11. Público-alvo sugerido
12. Avaliação crítica: por que vale a pena, valor prático, impacto profissional esperado, limitações

ORDENAÇÃO: Comece pelas 5 melhores oportunidades. Depois seção complementar se houver outras relevantes.

FECHAMENTO OBRIGATÓRIO:
- Top 3 recomendações da semana
- Melhor opção de curto prazo
- Melhor opção de ganho estratégico
- Melhor custo-benefício
- O que merece atenção mas talvez não valha meu tempo agora

Use linguagem clara, objetiva, executiva, orientada à decisão. Quero curadoria crítica e estratégica, não lista simples."""

def run():
    today = datetime.now().strftime("%d/%m/%Y")
    print(f"📊 Gerando relatório de cursos — {today}")
    
    try:
        result = subprocess.run(
            ["openclaw", "ask", "--no-stream", PROMPT],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Erro ao gerar relatório: {result.stderr}"
    except Exception as e:
        return f"Erro: {e}"

if __name__ == "__main__":
    report = run()
    print(report)
