# aesthetic-thief

Skill + pipeline local (Playwright/CDP + Python) para capturar estéticas reais da web, extrair tokens computados e animações, e remixar múltiplas direções por **camadas arquiteturais** sem virar Frankenstein.

## Como funciona

1. **Captura (`tools/extract_aesthetic.py`):** abre as URLs alvo em Edge/Chromium headless (`1440x900` e `375x812`), salva screenshots, coleta `getComputedStyle`, variáveis `--*` e `document.getAnimations()`.
2. **Show & Tell:** você inspeciona os prints e o `AESTHETIC_REPORT.md` antes de qualquer código novo.
3. **Layer Mixer (`tools/blend_layers.py`):** atribui cada estética a uma camada exclusiva (`structure`, `surface`, `accent`, `micro`), gerando um `DESIGN_SPEC.md` canônico.
4. **Build + Anti-Slop:** integra com [`human-craft-frontend`](https://github.com/santanaluiz181-cell/human-craft-frontend) e `antislop` para gerar e validar o novo repositório.

## Uso rápido

```bash
# Instalar a skill
npx skills add santanaluiz181-cell/aesthetic-thief

# 1. Capturar referências
python tools/extract_aesthetic.py https://example.com --out ./captured

# 2. Remixar 4 estéticas por camada (25% cada)
python tools/blend_layers.py \
  --structure claude-editorial \
  --surface antigravity \
  --accent handmade-ink \
  --micro cli-pixel \
  --out DESIGN_SPEC.md
```

## Testes

```bash
python -m unittest discover -s tests -v
```
