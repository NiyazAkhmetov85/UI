import streamlit as st
import pandas as pd
import numpy as np

from utils.logs_manager import LogsManager
from utils.session_state_manager import SessionStateManager

class PSDCalculator:
    """
    Класс для расчета P(x) (рассчитанные) и формирования PSD-таблицы.
    """
    def __init__(self, session_manager: SessionStateManager, logs_manager: LogsManager):
        self.session_manager = session_manager
        self.logs_manager = logs_manager

    def run_calculations(self):
        """
        Запускает расчёты P(x) рассчитанные и обновляет таблицу PSD.
        """
        self.calculate_p_x_calculated()
        self.update_psd_table()

    def calculate_p_x_calculated(self):
        """
        Рассчитывает P(x) рассчитанные на основе параметров БВР.
        """
        try:
            x_values = st.session_state.get("x_values", [])
            if not x_values:
                st.sidebar.error("Ошибка: x_values не найдены.")
                return

            params = st.session_state.get("calculation_results", {})
            x_max = params.get("x_max", 1000)
            x_50 = params.get("x_50", 200)
            b = params.get("b", 3.5)

            # Удаление старых данных перед записью новых
            st.session_state.pop("P_x_calculated", None)

            p_x_calculated = [
                (x, (1 / (1 + (np.log(x_max / x) / np.log(x_max / x_50)) ** b)) * 100)
                for x in x_values if x <= x_max
            ]

            df = pd.DataFrame(p_x_calculated, columns=["Размер фрагмента (x), мм", "P(x) рассчитанные, %"])
            st.session_state["P_x_calculated"] = df
            st.sidebar.success("P(x) рассчитанные успешно вычислены.")
            self.logs_manager.add_log("psd_calculator", "P(x) рассчитанные успешно вычислены.", "успех")

        except Exception as e:
            st.sidebar.error(f"Ошибка при расчете P(x) рассчитанные: {e}")
            self.logs_manager.add_log("psd_calculator", f"Ошибка при расчете P(x) рассчитанные: {e}", "ошибка")

    def update_psd_table(self):
        """
        Обновляет таблицу PSD в session_state.
        """
        try:
            df = st.session_state.get("P_x_calculated")
            if not isinstance(df, pd.DataFrame) or df.empty:
                self.logs_manager.add_log(
                    "psd_calculator", "Ошибка: отсутствуют данные P_x_calculated для обновления PSD.", "ошибка"
                )
                return

            # Удаление старых данных перед записью новых
            st.session_state.pop("psd_table_calculated", None)

            df_sorted = df.sort_values(by="Размер фрагмента (x), мм", ascending=True).reset_index(drop=True)
            st.session_state["psd_table_calculated"] = df_sorted
            st.sidebar.success("Таблица PSD успешно обновлена!")
            self.logs_manager.add_log("psd_calculator", "Таблица PSD обновлена.", "успех")

        except Exception as e:
            self.logs_manager.add_log("psd_calculator", f"Ошибка обновления PSD: {e}", "ошибка")
