import sys
import json
import comtrade_ui
import Comtrade_backend
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLineEdit, QComboBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = comtrade_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.reporters = []
        self.partners = []
        self.commodities = []
        self.periods = []
        self.ui.invalid_periods_range_warning.hide()
        self.ui.invalid_commdities_range_warning.hide()
        self.ui.download_data_btn.hide()
        self.ui.success_lbl.hide()

        try:
            with open('subscription_key.txt', 'r') as subscription_file:
                self.subscription = subscription_file.read()
                self.ui.subscr_key_input.setText(self.subscription)
        except FileNotFoundError:
            self.subscription = None

        with open('reporter_codes_dict.txt', 'r') as input_file:
            reporters_dict = json.loads(input_file.read())
        self.ui.reporters_cmbbox.addItems(tuple((reporters_dict.keys())))

        with open('partner_codes_dict.txt', 'r') as input_file:
            partners_dict = json.loads(input_file.read())
        self.ui.partners_cmbbox.addItems(tuple((partners_dict.keys())))

        self.period_cmbboxes = [self.ui.periods_cmbbox, self.ui.periods_range_start_cmbbox,
                                self.ui.periods_range_end_cmbbox]


        commodities_range = list(map(str, list(range(1, 98))))
        self.commodities_cmbboxes = [self.ui.commodities_cmbbox, self.ui.commodities_range_start_cmbbox,
                                     self.ui.commodities_range_end_cmbbox]
        for cmbbox in self.commodities_cmbboxes:
            cmbbox.addItems(commodities_range)
        commodities_range_total = ['TOTAL'] + list(map(str, list(range(1, 98))))
        self.ui.commodities_cmbbox.clear()
        self.ui.commodities_cmbbox.addItems(commodities_range_total)

        self.ui.trade_freq_cmbbox.currentTextChanged.connect(self.trade_frequency_changed)
        self.ui.add_period_btn.clicked.connect(lambda: self.add_item_btn_clicked(self.ui.periods_cmbbox, self.periods))
        self.ui.add_partner_btn.clicked.connect(
            lambda: self.add_item_btn_clicked(self.ui.partners_cmbbox, self.partners))
        self.ui.add_reporter_btn.clicked.connect(
            lambda: self.add_item_btn_clicked(self.ui.reporters_cmbbox, self.reporters))
        self.ui.add_commodity_btn.clicked.connect(
            lambda: self.add_item_btn_clicked(self.ui.commodities_cmbbox, self.commodities))
        self.ui.add_periods_range_btn.clicked.connect(self.add_periods_range_btn_clicked)
        self.ui.add_commodities_range_btn.clicked.connect(self.add_commodities_range_btn_clicked)
        self.ui.csv_rdbtn.clicked.connect(self.csv_rdbtn_clicked)
        self.ui.xlsx_rdbtn.clicked.connect(self.xlsx_rdbtn_clicked)
        self.ui.output_file_name_input.textEdited.connect(self.output_file_name_inputted)
        self.ui.download_data_btn.clicked.connect(self.download_data_btn_clicked)

    def trade_frequency_changed(self):
        for cmbbox in [self.ui.periods_cmbbox, self.ui.periods_range_start_cmbbox,
                       self.ui.periods_range_end_cmbbox]:
            cmbbox.clear()
        if self.ui.trade_freq_cmbbox.currentText() == 'Yearly':
            for cmbbox in [self.ui.periods_cmbbox, self.ui.periods_range_start_cmbbox,
                           self.ui.periods_range_end_cmbbox]:
                cmbbox.addItems(map(str, list(range(1962, 2024))))
        elif self.ui.trade_freq_cmbbox.currentText() == 'Monthly':
            for cmbbox in [self.ui.periods_cmbbox, self.ui.periods_range_start_cmbbox,
                           self.ui.periods_range_end_cmbbox]:
                months = []
                for year in map(str, list(range(2010, 2024))):
                    for month in map(str, list(range(1, 13))):
                        if len(month) == 1:
                            month = '0' + month
                        period = year + month
                        months.append(period)
                cmbbox.addItems(months)

    @staticmethod
    def add_item_btn_clicked(cmbbox, items_list):
        item = cmbbox.currentText()
        items_list.append(item)
        cmbbox.removeItem(cmbbox.findText(item))

    def add_periods_range_btn_clicked(self):
        if int(self.ui.periods_range_end_cmbbox.currentText()) < int(self.ui.periods_range_start_cmbbox.currentText()):
            self.ui.invalid_periods_range_warning.show()
            return
        if self.ui.trade_freq_cmbbox.currentText() == 'Yearly':
            period_range = list(map(str, range(int(self.ui.periods_range_start_cmbbox.currentText()),
                                               int(self.ui.periods_range_end_cmbbox.currentText()) + 1)))
            self.periods += period_range
            for period in period_range:
                for cmbbox in self.period_cmbboxes:
                    cmbbox.removeItem(cmbbox.findText(period))
        elif self.ui.trade_freq_cmbbox.currentText() == "Monthly":
            period =\
                f'{self.ui.periods_range_start_cmbbox.currentText()}-{self.ui.periods_range_end_cmbbox.currentText()}'
            period_range = Comtrade_backend.get_months_range(period, self.periods)
            self.periods += period_range
            for period in period_range:
                for cmbbox in self.period_cmbboxes:
                    cmbbox.removeItem(cmbbox.findText(period))

    def add_commodities_range_btn_clicked(self):
        if int(self.ui.commodities_range_end_cmbbox.currentText()) <\
                int(self.ui.commodities_range_start_cmbbox.currentText()):
            self.ui.invalid_commdities_range_warning.show()
            return
        self.ui.invalid_commdities_range_warning.hide()
        commodities_range = list(map(str, range(int(self.ui.commodities_range_start_cmbbox.currentText()),
                                                int(self.ui.commodities_range_end_cmbbox.currentText()) + 1)))
        for commodity in commodities_range:
            for cmbbox in self.commodities_cmbboxes:
                cmbbox.removeItem(cmbbox.findText(commodity))
        commodities_range = ['0' + acode if len(acode) == 1 else acode for acode in commodities_range]
        self.commodities += commodities_range

    def csv_rdbtn_clicked(self):
        self.ui.hs_group_chckbox.setChecked(False)
        self.ui.hs_group_chckbox.setDisabled(True)

    def xlsx_rdbtn_clicked(self):
        self.ui.hs_group_chckbox.setEnabled(True)

    def output_file_name_inputted(self):
        self.ui.download_data_btn.show()

    def download_data_btn_clicked(self):
        trade_freq_dict = {'Yearly': 'A',
                           'Monthly': 'M'}
        trade_freq = trade_freq_dict[self.ui.trade_freq_cmbbox.currentText()]
        flow_codes_dict = {'Export': 'X',
                           'Import': 'M',
                           'Both': r'X,M'}
        flow_codes = flow_codes_dict[self.ui.flow_cmbbox.currentText()]
        aggregate_by_dict = {'': None,
                             'By commodity': 'cmdCode',
                             'By period': 'period',
                             'By reporter': 'reporterCode',
                             'By partner': 'partnerCode'}
        aggregate_by = aggregate_by_dict[self.ui.aggregate_by_cmbbox.currentText()]
        self.reporters = sorted(self.reporters)
        self.partners = sorted(self.partners)
        self.periods = sorted(self.periods, key=lambda x: int(x))
        self.commodities = sorted(self.commodities)
        params, list_by_twelve_periods = Comtrade_backend.get_inputs(trade_freq, self.reporters, self.partners,
                                                                     self.periods, self.commodities, flow_codes,
                                                                     aggregate_by)
        df = Comtrade_backend.create_dataframe(params, trade_freq,
                                               list_by_twelve_periods, self.ui.subscr_key_input.text())
        df = Comtrade_backend.sort_dataframe(df)
        df = Comtrade_backend.clean_data_hs_sitc(df)
        output_file_name = self.ui.output_file_name_input.text()
        if self.ui.xlsx_rdbtn.isChecked():
            Comtrade_backend.save_df(df, output_file_name, 'xlsx')
        else:
            Comtrade_backend.save_df(df, output_file_name, 'csv')

        if self.ui.hs_group_chckbox.isChecked():
            Comtrade_backend.group_by_hs_chapters(df, f'{output_file_name} sorted')
        with open('subscription_key.txt', 'w') as subscription_file:
            subscription_file.write(self.ui.subscr_key_input.text())
        self.ui.success_lbl.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
