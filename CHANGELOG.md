# Changelog

Todas as mudanças importantes deste projeto serão documentadas aqui.

O formato segue o padrão **Keep a Changelog**  
e **Semantic Versioning (SemVer)**.

---

## [0.2.0] - 2025-02-14

### Adicionado

- Parametrização de “Valor Sigiloso?” (Sim/Não).
- Parametrização de “Tipo de Benefício da LCP 123/2006”.
- Nova estrutura de logging em CSV, gerando arquivos timestampados.
- Resumo final com contagem de itens processados/pulados/erros.
- Tratamento automático de pop-ups JavaScript com `alert.accept()`.
- Flags configuráveis:
  - `SALVAR_ITEM_DRY_RUN`
  - `DEFINIR_VALOR_SIGILOSO`
  - `DEFINIR_TIPO_BENEFICIO`
  - `REMOTE_DEBUGGING_PORT`
- Coleta dos campos:
  - Nº do item
  - Código + descrição
- Fluxo completo de ajustes para cada item, incluindo:
  - Tipo de Variação
  - Intervalo Mínimo entre Lances
  - Aquisição PAC
  - Permitir Adesões
- Melhorias no algoritmo de espera (wait) e tratamento de elementos instáveis.
- Funções utilitárias mais robustas, com retry automático.

### Modificado

- Lógica de salvar item agora aceita opção de dry-run.
- Lógica de navegação entre itens mais confiável.

---

## [0.1.0] - 2025-02-14

### Adicionado

- Versão inicial do projeto.
- Automação base usando Selenium + Chrome Remote Debugging.
- Detecção de inconsistências dos itens.
- Ajuste automático de:
  - Tipo de Variação
  - Intervalo Mínimo entre Lances
  - Aquisição PAC
  - Permitir Adesões
- Modo dry-run para evitar salvamento real.
- Navegação automática entre itens.
