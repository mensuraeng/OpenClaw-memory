# deploy-infra.md

## Escopo
Implantação, hardening, empacotamento e distribuição.

## Repositórios principais
- `openclaw/openclaw-ansible` — instalação automatizada e endurecida com Tailscale, UFW e isolamento por Docker.
- `openclaw/nix-openclaw` — empacotamento para Nix.
- `openclaw/homebrew-tap` — distribuição via Homebrew.
- `openclaw/clawdinators` — infraestrutura declarativa + módulos NixOS para hosts CLAWTINATOR.

## Quando consultar este arquivo
- instalação automatizada
- hardening
- deploy repetível
- empacotamento
- distribuição e ambientes

## Leitura correta
Infra não é detalhe lateral. Em OpenClaw, a qualidade do deploy altera estabilidade, segurança e capacidade real de operação.

## Regra prática
Se a dúvida for “como subir, distribuir, endurecer ou padronizar ambiente”, consultar esta frente.
