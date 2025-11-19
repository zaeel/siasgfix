# siasgfix

Automação especializada para corrigir inconsistências de itens em licitações no módulo de Divulgação de Compras do sistema **SIASGnet** (Comprasnet) do Governo Federal.  
O projeto utiliza **Selenium + Chrome Remote Debugging** para percorrer cada item da licitação, identificar inconsistências, aplicar parametrizações automáticas e registrar logs completos de cada execução.

---

## 🚀 Funcionalidades

- Detecta automaticamente itens com **Inconsistências do Item**.
- Configura campos essenciais como:
  - Valor Sigiloso (Sim/Não)
  - Tipo de Benefício da LCP 123/2006
  - Tipo de Variação
  - Intervalo mínimo entre lances
  - Aquisição PAC?
  - Permitir adesões?
- Trata automaticamente pop-ups do sistema (ex.: alerta de margem de preferência).
- Pode operar em **modo dry-run** (não salva no SIASG).
- Registra cada execução em CSV (timestamped).
- Suporta Chrome com **remote debugging** para evitar conflitos com o uso manual.

---

## 📦 Requisitos

- Python **3.9+**
- Google Chrome instalado
- Execução do Chrome com a flag `--remote-debugging-port`

Instale as dependências:

```bash
pip install -r requirements.txt
```

Conteúdo de `requirements.txt`:

```
selenium>=4.19.0
webdriver-manager>=4.0.0
```

---

## 🛠 Como usar

### 1. Abra o Chrome com o Remote Debugging habilitado

Crie (ou use) uma pasta separada para o perfil Selenium:

```bat
start chrome ^
  --user-data-dir="C:\temp\SeleniumDataDir" ^
  --remote-debugging-port=9222
```

Se preferir, pode usar o `launch_chrome.bat`.

> A porta (9222) é configurável no código.

### 2. Acesse o SIASGnet e carregue a listagem de itens da licitação (mantenha apenas uma aba aberta com essa página)

### 3. Execute o script Python

```bash
python main.py
```

O script irá:

1. Conectar ao Chrome já aberto
2. Ler a página ativa do SIASGnet
3. Iterar sobre os itens
4. Identificar itens com inconsistências
5. Aplicar ajustes conforme configurações
6. Registrar o log CSV em `comprasnet_log_YYYYMMDD-HHMMSS.csv`

---

## ⚙️ Configurações

No topo de `main.py`, você pode ajustar:

```python
REMOTE_DEBUGGING_PORT = 9222
SALVAR_ITEM_DRY_RUN = True
DEFINIR_VALOR_SIGILOSO = True
VALOR_SIGILOSO_VALUE = "2"
DEFINIR_TIPO_BENEFICIO = True
TIPO_BENEFICIO_VALUE = "-1"
TIPO_VARIACAO_VALUE = "2"
INTERVALO_MINIMO_VALOR = "100"
```

---

## 📁 Logs

A cada execução, um arquivo CSV será criado, com nome como:

```
comprasnet_log_20250214-223544.csv
```

O arquivo contém:

- Nº do item
- Código/Descrição
- Existência de inconsistências
- Se ajustes foram aplicados
- Se o botão “Salvar” foi acionado
- Erros (se houver)

---

## 📜 Licença

Este projeto é distribuído sob a licença **MIT**, permitindo livre uso, modificação e redistribuição.  
Veja mais em: [LICENSE](LICENSE)

---

## 🤝 Contribuições

Contribuições são bem-vindas!  
Sugestões, melhorias ou relatórios de erros podem ser enviados via _Issues_ ou _Pull Requests_.

---

## ⚠️ Aviso Legal

Este projeto não tem vínculo oficial com o Governo Federal, SIASG ou Comprasnet.  
É uma ferramenta auxiliar criada para uso administrativo e automatização de rotinas internas.

Seu uso deve respeitar as normas, restrições e responsabilidades aplicáveis ao sistema SIASGnet.

---
