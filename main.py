import csv
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# ==============================
# CONFIGURAÇÕES
# ==============================
TIPO_VARIACAO_VALUE = "2"  # 2 = Monetário (pode alterar)
INTERVALO_MINIMO_VALOR = "100"  # Intervalo Mínimo entre Lances
SALVAR_ITEM_DRY_RUN = True  # True = NÃO clicar em Salvar; False = clicar de verdade
REMOTE_DEBUGGING_PORT = 9222  # Porta usada no --remote-debugging-port

# NOVAS ETAPAS
DEFINIR_VALOR_SIGILOSO = False  # Se False, não mexe em "Valor Sigiloso?"
VALOR_SIGILOSO_VALUE = "2"  # "1" = Sim, "2" = Não

DEFINIR_TIPO_BENEFICIO = False  # Se False, não mexe em "Tipo de Benefício"
TIPO_BENEFICIO_VALUE = "1"  # "-1"=Sem Benefício, "1"=Tipo I, "2"=Tipo II, "3"=Tipo III


# ==============================
# DRIVER (Chrome via remote debugging)
# ==============================
def create_driver():
    options = Options()
    # Chrome aberto com algo como:
    # "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222
    options.add_experimental_option(
        "debuggerAddress", f"127.0.0.1:{REMOTE_DEBUGGING_PORT}"
    )

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(0)  # vamos trabalhar só com WebDriverWait
    return driver


# ==============================
# ESPERAR OVERLAY "AGUARDE" SUMIR
# ==============================
def wait_loading_overlay(driver, timeout=30):
    wait = WebDriverWait(driver, timeout)
    try:
        wait.until(EC.invisibility_of_element_located((By.ID, "frameloading")))
    except TimeoutException:
        pass


# ==============================
# ESPERAR O ITEM N ESPECÍFICO CARREGAR
# ==============================
def wait_item_loaded(driver, item_num, timeout=30):
    """
    Espera até que o campo #numeroItemNavegacao tenha o valor do item desejado.
    """
    wait = WebDriverWait(driver, timeout)

    def _item_is_loaded(d):
        try:
            elem = d.find_element(By.ID, "numeroItemNavegacao")
            val = elem.get_attribute("value")
            return val == str(item_num)
        except Exception:
            return False

    wait_loading_overlay(driver, timeout)
    wait.until(_item_is_loaded)


# ==============================
# LEITURAS COM RETRY (STABLE)
# ==============================
def get_numero_item(driver, wait, max_retry=5):
    for attempt in range(max_retry):
        try:
            elem = wait.until(
                EC.presence_of_element_located((By.NAME, "itemLicitacao.numeroItem"))
            )
            return elem.get_attribute("value").strip()
        except StaleElementReferenceException:
            if attempt == max_retry - 1:
                raise


def get_codigo_descricao(driver, wait, max_retry=5):
    for attempt in range(max_retry):
        try:
            codigo_elem = wait.until(
                EC.presence_of_element_located(
                    (By.NAME, "itemLicitacao.codigoItemCatalogo")
                )
            )
            desc_elem = wait.until(
                EC.presence_of_element_located((By.NAME, "itemLicitacao.descricao"))
            )
            codigo = codigo_elem.get_attribute("value").strip()
            descricao = desc_elem.get_attribute("value").strip()
            return f"{codigo} - {descricao}"
        except StaleElementReferenceException:
            if attempt == max_retry - 1:
                raise


# ==============================
# AÇÕES POR ITEM
# ==============================
def set_valor_sigiloso(driver, wait, valor=VALOR_SIGILOSO_VALUE, max_retry=5):
    """
    Define "Valor Sigiloso?" via radio:
    <input type="radio" name="itemLicitacao.valorCaraterSigiloso" value="1|2">
    """
    if not DEFINIR_VALOR_SIGILOSO:
        return

    for attempt in range(max_retry):
        try:
            elem = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f"//input[@name='itemLicitacao.valorCaraterSigiloso' and @value='{valor}']",
                    )
                )
            )
            elem.click()
            return
        except StaleElementReferenceException:
            if attempt == max_retry - 1:
                raise


def set_tipo_beneficio(driver, wait, tipo_value=TIPO_BENEFICIO_VALUE, max_retry=5):
    """
    Define "Tipo de Benefício" no select:
    <select id="idTipoBeneficio" name="tipoBeneficio">...
    """
    if not DEFINIR_TIPO_BENEFICIO:
        return

    for attempt in range(max_retry):
        try:
            elem = wait.until(EC.element_to_be_clickable((By.ID, "idTipoBeneficio")))
            select = Select(elem)
            select.select_by_value(tipo_value)
            return
        except StaleElementReferenceException:
            if attempt == max_retry - 1:
                raise


def set_tipo_variacao(driver, wait, tipo_value=TIPO_VARIACAO_VALUE, max_retry=5):
    for attempt in range(max_retry):
        try:
            elem = wait.until(EC.element_to_be_clickable((By.ID, "idComboTipoReducao")))
            select = Select(elem)
            select.select_by_value(tipo_value)
            return
        except StaleElementReferenceException:
            if attempt == max_retry - 1:
                raise


def set_intervalo_minimo_lances(
    driver, wait, valor=INTERVALO_MINIMO_VALOR, max_retry=5
):
    for attempt in range(max_retry):
        try:
            elem = wait.until(
                EC.element_to_be_clickable(
                    (By.NAME, "itemLicitacao.intervaloMinimoEntreLances")
                )
            )
            elem.clear()
            elem.send_keys(valor)
            return
        except StaleElementReferenceException:
            if attempt == max_retry - 1:
                raise


def marcar_aquisicao_pac_nao(driver, wait, max_retry=5):
    for attempt in range(max_retry):
        try:
            elem = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//input[@name='itemLicitacao.aquisicaoPac' and @value='2']",
                    )
                )
            )
            elem.click()
            return
        except StaleElementReferenceException:
            if attempt == max_retry - 1:
                raise


def marcar_permitir_adesoes_nao(driver, wait, max_retry=5):
    for attempt in range(max_retry):
        try:
            elem = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@name='permitirAdesaoAta' and @value='2']")
                )
            )
            elem.click()
            return
        except StaleElementReferenceException:
            if attempt == max_retry - 1:
                raise


def item_tem_inconsistencias(driver):
    fieldsets = driver.find_elements(
        By.XPATH, "//fieldset[legend[normalize-space()='Inconsistências do Item']]"
    )
    return any(fs.is_displayed() for fs in fieldsets)


def salvar_item(driver, wait, item_num, max_retry=5):
    """
    Ação de salvar com tratamento de popup JS.
    Retorna True se o clique foi realmente executado.
    """
    for attempt in range(max_retry):
        try:
            elem = wait.until(EC.element_to_be_clickable((By.ID, "salvar")))

            if SALVAR_ITEM_DRY_RUN:
                print(
                    f"[DRY-RUN] Item {item_num}: botão 'Salvar Item' localizado, "
                    f"mas clique NÃO foi executado (SALVAR_ITEM_DRY_RUN=True)."
                )
                return False

            print(f"[AÇÃO] Item {item_num}: clicando em 'Salvar Item'...")
            elem.click()

            # Tenta capturar alerta imediatamente
            try:
                alerta = driver.switch_to.alert
                texto = alerta.text
                print(f"[INFO] Alerta detectado: {texto}")
                alerta.accept()
                print("[AÇÃO] Pop-up confirmado com OK.")
            except Exception:
                pass

            wait_loading_overlay(driver)
            wait_item_loaded(driver, item_num)
            return True

        except UnexpectedAlertPresentException:
            alerta = driver.switch_to.alert
            texto = alerta.text
            print(f"[INFO] Alerta detectado (via exceção): {texto}")
            alerta.accept()
            print("[AÇÃO] Pop-up confirmado com OK.")

            wait_loading_overlay(driver)
            wait_item_loaded(driver, item_num)
            return True

        except StaleElementReferenceException:
            if attempt == max_retry - 1:
                raise


def ir_para_proximo_item(driver, wait, item_num, max_retry=5):
    for attempt in range(max_retry):
        try:
            btn_proximo = wait.until(
                EC.element_to_be_clickable((By.ID, "btnProximoItem"))
            )
            print(f"[AÇÃO] Indo para o próximo item (atual: {item_num})...")
            btn_proximo.click()
            return
        except (StaleElementReferenceException, TimeoutException):
            if attempt == max_retry - 1:
                print("[ERRO] Não foi possível clicar em 'Próximo Item'.")
                raise


# ==============================
# PROGRAMA PRINCIPAL
# ==============================
def main():
    driver = create_driver()
    wait = WebDriverWait(driver, 20)

    wait_loading_overlay(driver)
    qtd_elem = wait.until(
        EC.presence_of_element_located(
            (By.NAME, "versaoCompraComLicitacao.quantidadeItens")
        )
    )
    qtd_itens = int(qtd_elem.get_attribute("value").strip())
    print(f"[INFO] Quantidade de itens: {qtd_itens}")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    csv_filename = f"comprasnet_log_{timestamp}.csv"

    total_processados = 0
    total_pulados = 0
    total_erros = 0

    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "item_index_loop",
                "numero_item",
                "codigo_descricao",
                "had_inconsistencias",
                "ajustado",
                "salvar_executado",
                "mensagem_erro",
            ]
        )

        for idx in range(qtd_itens):
            item_num = idx + 1
            print(f"\n===== ITEM {item_num} =====")

            try:
                wait_item_loaded(driver, item_num)

                numero_item = get_numero_item(driver, wait)
                cod_descr = get_codigo_descricao(driver, wait)

                has_incons = item_tem_inconsistencias(driver)

                if not has_incons:
                    print(
                        f"[INFO] Item {item_num} não possui 'Inconsistências do Item'. Pulando ajustes."
                    )
                    writer.writerow(
                        [item_num, numero_item, cod_descr, False, False, False, ""]
                    )
                    total_pulados += 1

                    if item_num < qtd_itens:
                        ir_para_proximo_item(driver, wait, item_num)
                    continue

                print(f"Nº do item: {numero_item}")
                print(f"Código/Descrição: {cod_descr}")

                # 1) Valor sigiloso (opcional)
                set_valor_sigiloso(driver, wait, VALOR_SIGILOSO_VALUE)

                # 2) Tipo de benefício (opcional)
                set_tipo_beneficio(driver, wait, TIPO_BENEFICIO_VALUE)

                # 3) Tipo de variação
                set_tipo_variacao(driver, wait, TIPO_VARIACAO_VALUE)

                # 4) Intervalo mínimo entre lances
                set_intervalo_minimo_lances(driver, wait, INTERVALO_MINIMO_VALOR)

                # 5) Aquisição PAC? = Não
                marcar_aquisicao_pac_nao(driver, wait)

                # 6) Permitir adesões? = Não
                marcar_permitir_adesoes_nao(driver, wait)

                # 7) Salvar
                salvar_executado = salvar_item(driver, wait, item_num)

                writer.writerow(
                    [item_num, numero_item, cod_descr, True, True, salvar_executado, ""]
                )
                total_processados += 1

                # 8) Próximo item
                if item_num < qtd_itens:
                    ir_para_proximo_item(driver, wait, item_num)

            except Exception as e:
                msg = str(e)
                print(f"[ERRO] Item {item_num}: {msg}")
                writer.writerow(
                    [
                        item_num,
                        locals().get("numero_item", ""),
                        locals().get("cod_descr", ""),
                        "",
                        False,
                        False,
                        msg,
                    ]
                )
                total_erros += 1

                if item_num < qtd_itens:
                    try:
                        ir_para_proximo_item(driver, wait, item_num)
                    except Exception:
                        break

    print("\n===== RESUMO DA EXECUÇÃO =====")
    print(f"Arquivo de log: {csv_filename}")
    print(f"Itens total: {qtd_itens}")
    print(f"Itens com inconsistências processados: {total_processados}")
    print(f"Itens pulados (sem inconsistências): {total_pulados}")
    print(f"Itens com erro: {total_erros}")
    print(f"SALVAR_ITEM_DRY_RUN = {SALVAR_ITEM_DRY_RUN}")
    print(
        f"DEFINIR_VALOR_SIGILOSO = {DEFINIR_VALOR_SIGILOSO} (valor={VALOR_SIGILOSO_VALUE})"
    )
    print(
        f"DEFINIR_TIPO_BENEFICIO = {DEFINIR_TIPO_BENEFICIO} (valor={TIPO_BENEFICIO_VALUE})"
    )

    # driver.quit()  # opcional


if __name__ == "__main__":
    main()
