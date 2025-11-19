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
INTERVALO_MINIMO_VALOR = "100"  # Intervalo Mínimo entre Lances (pode alterar)
SALVAR_ITEM_DRY_RUN = False  # True = NÃO clicar em Salvar; False = clicar de verdade
REMOTE_DEBUGGING_PORT = 9222  # Porta usada no --remote-debugging-port


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
        # Se não existir ou não sumir, segue mesmo assim
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

    # Primeiro garante que o overlay (se houver) sumiu
    wait_loading_overlay(driver, timeout)

    # Depois espera o número do item mudar/confirmar
    wait.until(_item_is_loaded)


# ==============================
# LEITURAS COM RETRY (STABLE)
# ==============================
def get_numero_item(driver, wait, max_retry=5):
    """
    Lê o Nº do item:
    <input name="itemLicitacao.numeroItem" ...>
    """
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
    """
    Lê o código e descrição:
    <input name="itemLicitacao.codigoItemCatalogo" ...>
    <input name="itemLicitacao.descricao" ...>
    Retorna string no formato: "442145 - Agulha Odontológica"
    """
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
def set_tipo_variacao(driver, wait, tipo_value=TIPO_VARIACAO_VALUE, max_retry=5):
    """
    Define o Tipo de Variação:
    <select id="idComboTipoReducao" name="itemLicitacao.tipoReducao">...
    """
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
    """
    Preenche:
    <input name="itemLicitacao.intervaloMinimoEntreLances" ...>
    """
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
    """
    Marca:
    <input type="radio" name="itemLicitacao.aquisicaoPac" value="2"> (Não)
    """
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
    """
    Marca:
    <input type="radio" name="permitirAdesaoAta" value="2"> (Não)
    """
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
    """
    Verifica se existe fieldset com:
    <legend>Inconsistências do Item</legend>
    Se NÃO existir, o item está OK e pode ser pulado.
    """
    fieldsets = driver.find_elements(
        By.XPATH, "//fieldset[legend[normalize-space()='Inconsistências do Item']]"
    )
    return any(fs.is_displayed() for fs in fieldsets)


def salvar_item(driver, wait, item_num, max_retry=5):
    """
    Ação 5: clicar em 'Salvar Item'.
    - Se SALVAR_ITEM_DRY_RUN = True: não clica, apenas loga.
    - Se SALVAR_ITEM_DRY_RUN = False: clica e aguarda carregamento.
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

            # Clique real
            print(f"[AÇÃO] Item {item_num}: clicando em 'Salvar Item'...")
            elem.click()

            # Tentativa de lidar com popup imediatamente após o clique
            try:
                alerta = driver.switch_to.alert
                texto = alerta.text
                print(f"[INFO] Alerta detectado: {texto}")
                alerta.accept()  # Clicar em OK
                print("[AÇÃO] Pop-up confirmado com OK.")
            except:
                # Nenhum alerta apareceu, o que é normal na maioria dos itens
                pass

            # Aguarda página recarregar
            wait_loading_overlay(driver)
            wait_item_loaded(driver, item_num)
            return True

        except UnexpectedAlertPresentException:
            # Alerta capturado no meio do clique
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
    """
    Clica no botão 'Próximo Item'.
    """
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

    # Se for testar local:
    # driver.get("file:///C:/caminho/dump.html")

    # 1) Ler quantidade de itens
    wait_loading_overlay(driver)
    qtd_elem = wait.until(
        EC.presence_of_element_located(
            (By.NAME, "versaoCompraComLicitacao.quantidadeItens")
        )
    )
    qtd_itens = int(qtd_elem.get_attribute("value").strip())
    print(f"[INFO] Quantidade de itens: {qtd_itens}")

    # 2) Preparar arquivo CSV de log
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

        # 3) Loop pelos itens
        for idx in range(qtd_itens):
            item_num = idx + 1
            print(f"\n===== ITEM {item_num} =====")

            try:
                # Espera o item correto carregar
                wait_item_loaded(driver, item_num)

                # Sempre lê nº do item e código/descrição (para log, mesmo se pular)
                numero_item = get_numero_item(driver, wait)
                cod_descr = get_codigo_descricao(driver, wait)

                # Verifica se há inconsistências
                has_incons = item_tem_inconsistencias(driver)

                if not has_incons:
                    print(
                        f"[INFO] Item {item_num} não possui 'Inconsistências do Item'. Pulando ajustes."
                    )
                    writer.writerow(
                        [
                            item_num,
                            numero_item,
                            cod_descr,
                            False,  # had_inconsistencias
                            False,  # ajustado
                            False,  # salvar_executado
                            "",  # mensagem_erro
                        ]
                    )
                    total_pulados += 1

                    if item_num < qtd_itens:
                        ir_para_proximo_item(driver, wait, item_num)
                    continue

                # Log básico
                print(f"Nº do item: {numero_item}")
                print(f"Código/Descrição: {cod_descr}")

                # 1) Definir Tipo de Variação (Monetário por padrão)
                set_tipo_variacao(driver, wait, TIPO_VARIACAO_VALUE)

                # 2) Preencher Intervalo Mínimo entre Lances
                set_intervalo_minimo_lances(driver, wait, INTERVALO_MINIMO_VALOR)

                # 3) Marcar "É uma aquisição PAC?" = Não (value="2")
                marcar_aquisicao_pac_nao(driver, wait)

                # 4) Marcar "Permitir Adesões" = Não (value="2")
                marcar_permitir_adesoes_nao(driver, wait)

                # 5) Salvar Item (comportamento controlado por SALVAR_ITEM_DRY_RUN)
                salvar_executado = salvar_item(driver, wait, item_num)

                writer.writerow(
                    [
                        item_num,
                        numero_item,
                        cod_descr,
                        True,  # had_inconsistencias
                        True,  # ajustado
                        salvar_executado,  # salvar_executado
                        "",  # mensagem_erro
                    ]
                )
                total_processados += 1

                # 6) Próximo item (se não for o último)
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
                        "",  # had_inconsistencias desconhecido
                        False,  # ajustado
                        False,  # salvar_executado
                        msg,  # mensagem_erro
                    ]
                )
                total_erros += 1

                # Tenta seguir para o próximo item, se possível
                if item_num < qtd_itens:
                    try:
                        ir_para_proximo_item(driver, wait, item_num)
                    except Exception:
                        # Se nem isso for possível, interrompe o loop
                        break

    # ==============================
    # RESUMO FINAL
    # ==============================
    print("\n===== RESUMO DA EXECUÇÃO =====")
    print(f"Arquivo de log: {csv_filename}")
    print(f"Itens total: {qtd_itens}")
    print(f"Itens com inconsistências processados: {total_processados}")
    print(f"Itens pulados (sem inconsistências): {total_pulados}")
    print(f"Itens com erro: {total_erros}")
    print(f"SALVAR_ITEM_DRY_RUN = {SALVAR_ITEM_DRY_RUN}")

    # driver.quit()  # opcional


if __name__ == "__main__":
    main()
