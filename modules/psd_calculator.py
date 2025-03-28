import streamlit as st
import pandas as pd
import numpy as np
from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager

class PSDCalculator:
    """
    Класс для расчета P(x) (рассчитанные) и формирования PSD-таблицы.
    """
    def __init__(self, session_manager: SessionStateManager):
        self.session_manager = session_manager
        self.logs_manager = LogsManager(session_manager)

    def run_calculations(self):
        """
        Запускает расчёты P(x) рассчитанные и обновляет таблицу PSD.
        """
        self.session_manager.set_state("current_step", "Запуск расчетов PSD")
        st.session_state["status_message"] = "Запуск расчетов PSD..."

        try:
            # ✅ Рассчитываем P(x) рассчитанные
            self.calculate_p_x_calculated()
            
            # ✅ Генерируем PSD-таблицу
            self.generate_psd_table()

            self.logs_manager.add_log("psd_calculator", "✅ Все расчёты PSD успешно выполнены.", "успех")
            st.success("✅ Все расчёты PSD успешно выполнены и сохранены.")

        except Exception as e:
            self.logs_manager.add_log("psd_calculator", f"Ошибка при расчетах PSD: {str(e)}", "ошибка")
            st.error(f"❌ Ошибка при выполнении расчетов PSD: {e}")

        finally:
            self.session_manager.set_state("current_step", None)
            st.session_state["status_message"] = "Готов к работе"

    def calculate_p_x_calculated(self):
        """
        Рассчитывает P(x) рассчитанные на основе параметров БВР.
        """
        try:
            x_values = st.session_state.get("x_values", [])
            if not x_values:
                st.error("Ошибка: x_values не найдены.")
                return

            params = st.session_state.get("calculation_results", {})
            x_max = params.get("x_max", 1000)
            x_50 = params.get("x_50", 200)
            b = params.get("b", 3.5)

            p_x_calculated = [(x, (1 / (1 + (np.log(x_max / x) / np.log(x_max / x_50)) ** b)) * 100) for x in x_values if x <= x_max]

            df = pd.DataFrame(p_x_calculated, columns=["Размер фрагмента (x), мм", "P(x) рассчитанные, %"])
            st.session_state["P_x_calculated"] = df
            self.logs_manager.add_log("psd_calculator", "P(x) рассчитанные успешно вычислены.", "успех")

        except Exception as e:
            st.error(f"Ошибка при расчете P(x) рассчитанные: {e}")
            self.logs_manager.add_log("psd_calculator", f"Ошибка при расчете P(x) рассчитанные: {e}", "ошибка")

    def generate_psd_table(self):
        """
        Формирует итоговую таблицу PSD.
        """
        try:
            df_reference = st.session_state.get("P_x_data")
            df_calculated = st.session_state.get("P_x_calculated")
            df_psd = pd.merge(df_reference, df_calculated, on="Размер фрагмента (x), мм", how="outer").fillna(0)
            st.session_state["psd_table"] = df_psd

            self.logs_manager.add_log("psd_calculator", "PSD-таблица успешно сформирована.", "успех")
            st.dataframe(df_psd)

        except Exception as e:
            st.error(f"Ошибка при создании PSD-таблицы: {e}")
