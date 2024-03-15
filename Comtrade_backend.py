import pandas as pd
import requests
import json
import time
import os


class Timer:
    """Class counting time for execution of the code.
    ----
    Attributes:
    - _start_time
    ----
    Methods:
    - start. Starts the timer counting
    - stop. Calculates elapsed time
    """

    def __init__(self):
        self._start_time = None

    def start(self):
        """Save the time at the beginning of execution to _start_time attribute."""
        self._start_time = time.perf_counter()

    def stop(self):
        """Calculate difference between the time when calling and the _start_time."""
        elapsed_time = time.perf_counter() - self._start_time
        print(f'The execution took {elapsed_time:0.4f} seconds')


def handle_exceptions(func: callable) -> callable:
    """
    Decorator, catches all types of exceptions and calls the function again, if one is raised.
    :param func: function to be wrapped in the exception handler
    :return: wrapped function
    """

    def wrapper(*args):
        try:
            res = func(*args)
        except Exception as error:
            catch_indefinite_exceptions(error)
            res = wrapper(*args)
        return res

    return wrapper


def catch_indefinite_exceptions(error: Exception) -> None:
    """
    Prints information about an exception and save it to a log file.
    :param error: error to be catched
    :return: None
    """
    print(f'''The following error occurred:
{error}''')


# The info is saved to errors_log.txt\n''')
#     with open('errors_log.txt', 'a') as errors_file:
#         errors_file.write(f'''
# The line number was: {inspect.currentframe().f_back.f_lineno}
# The error was: {error}
# The error type was: {type(error)}\n\n\n''')


def get_inputs(trade_frequency: str, reporters_list: list, partners_list: list, periods_list: list, cmd_list: list,
               flow_codes: str, aggregate_by: str) -> tuple[dict, list]:
    """Gets input data for the http request (trade type, trade frequency, classification of goods,
    reporter codes, partner codes, commodity codes, flow codes, aggregating methods).
    Returns parameters to include in the url,
    list of lists by twelve periods to use later when making requests and trade classification code.
    (UN Comtrade allows only to pass 12 periods simultaneously into request)"""

    reporter_codes = get_countries_codes('reporter_codes_dict.txt', reporters_list)
    partner_codes = get_countries_codes('partner_codes_dict.txt', partners_list)

    try:
        list_by_twelve_periods = get_periods(periods_list, 6, get_months_range)
    except IndexError:
        list_by_twelve_periods = get_periods(periods_list, 4, get_years_range)

    params = {'typeCode': 'C', 'freqCode': trade_frequency,
              'clCode': 'HS',
              'reporterCode': reporter_codes, 'cmdCode': ','.join(cmd_list),
              'flowCode': flow_codes, 'partnerCode': partner_codes,
              'format_output': 'JSON', 'partner2Code': None,
              'customsCode': None, 'motCode': None, 'aggregateBy': aggregate_by,
              'breakdownMode': 'classic', 'includeDesc': True}
    return params, list_by_twelve_periods


def get_countries_codes(file_name: str, countries_list: list) -> str:
    """Takes country names as inputs and load dictionaries {country_name: country_code} from files.
    Returns a string with respective comma-separated country codes for the request.
    Raises error if an invalid country name is inputted."""

    with open(file_name) as input_codes:
        codes_dict = json.loads(input_codes.read())
        codes_list = [codes_dict[country.strip()] for country in countries_list]
        country_codes = ','.join(codes_list)

    return country_codes


def get_periods(periods_input: list, length_of_single_period: int, range_getter: callable) -> list:
    """Gets periods as inputs, check their validity and return a list of lists by twelve periods."""

    periods_list = []
    for period in periods_input:
        period = period.strip()
        if len(period) == length_of_single_period:
            periods_list.append(period)
        else:
            periods_list = range_getter(period, periods_list)
    twelve_periods = make_list_of_twelve(periods_list)

    return twelve_periods


def check_years_validity(years: list) -> None:
    """Checks if a valid year (1962-2023) is inputted. Raise error if a year is invalid."""

    for year in years:
        if int(year) < 1962 or int(year) > 2023:
            raise Exception('You have inputted an invalid year')


def check_monthly_periods_validity(periods: list) -> None:
    """Checks if a valid monthly period (201001-202312) is inputted. Raise error if a period is invalid."""

    for period in periods:
        if any((int(period[:4]) < 2010, int(period[:4]) > 2023,
                int(period[4:]) < 1, int(period[4:]) > 12)):
            raise Exception('You should input valid periods')


def get_years_range(period: str, periods_list: list) -> list:
    """Takes period range (for ex., 2000-2003) as a parameter and turn in into a list of years.
    Returns the list."""

    years = period.split('-')
    for year in range(int(years[0]), int(years[1]) + 1):
        periods_list.append(str(year))

    return periods_list


def get_months_range(period: str, periods_list: list) -> list:
    """Takes period range (for ex., 200002-200306) as a parameter and turn in into a list of monthly periods.
    Returns the list."""

    months = period.split('-')
    current_year = months[0][:4]
    current_month = months[0][4:]
    end_period = months[1]
    while current_year + current_month != end_period:
        periods_list.append(current_year + current_month)
        if current_month != '12':
            current_month = '0' + str(int(current_month) + 1)
            current_month = current_month[-2:]
        else:
            current_month = '01'
            current_year = str(int(current_year) + 1)
    periods_list.append(end_period)

    return periods_list


def make_list_of_twelve(input_list: list) -> list:
    """Takes raw period list as a parameter and turns it into a list of lists by twelve periods."""

    twelve_periods = []
    while len(input_list) > 12:
        alist = input_list[:12]
        input_list = input_list[12:]
        twelve_periods.append(alist)
    twelve_periods.append(input_list)

    return twelve_periods


def get_cmd_codes(input_codes: list) -> str:
    """Gets commodity codes as input, unpacks ranges and returns a list of codes as a string."""

    codes_list = []
    for code in input_codes:
        code = code.strip()
        if len(code) == 2 or code == 'TOTAL':
            codes_list.append(code)
        else:
            range_boundaries = code.split('-')
            codes_range = range(int(range_boundaries[0]),
                                int(range_boundaries[1]) + 1)
            for acode in codes_range:
                if len(str(acode)) == 2:
                    codes_list.append(str(acode))
                else:
                    codes_list.append('0' + str(acode))
    codes = ','.join(codes_list)

    return codes


def create_dataframe(params: dict, frequency: str, list_by_twelve_periods: list,
                     subscription_key: str) -> pd.DataFrame:
    """Takes parameters for the request and periods as input. Returns dataframe obtained through the request."""
    for alist in list_by_twelve_periods:
        params['period'] = ','.join(alist)
        headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Cookie': "_ga_LV1D7W0C7B=GS1.2.1691785074.1.0.1691785074.0.0.0; _ga=GA1.1.1712479289.1691785074; _ga_4TQXCK3CPF=GS1.1.1691785079.1.1.1691786152.0.0.0; _ga_FQGEEQQBB2=GS1.1.1691785079.1.1.1691786153.0.0.0; SL_G_WPT_TO=ru; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1"}
        # params = urllib.parse.urlencode(params, safe=',')
        print('try to get')
        try:
            response = requests.get(url=f'https://comtradeapi.un.org/data/v1/get/C/{frequency}/HS', headers=headers,
                                    params=params, timeout=200)
            print(response.status_code)
            print(response.url)
            try:
                # small_df = comtradeapicall.getFinalData(subscription_key,
                #                                         **params)
                small_df = pd.json_normalize(response.json()['data'])
                df = pd.concat([df, small_df])
            except NameError:
                # df = comtradeapicall.getFinalData(subscription_key, **params)
                df = pd.json_normalize(response.json()['data'])
            time.sleep(30)
        except requests.exceptions.Timeout:
            df = divide_response(headers, params)
    return df


def divide_response(headers: dict, params: dict) -> pd.DataFrame:
    """
    Divides the request into two smaller requests along the longest parameter.
    Args:
        headers: headers for the request
        params: parameters for the request

    Returns: Concatenated dataframe from two smaller responses

    """
    time.sleep(30)
    number_of_params = {}
    for param in ['reporterCode', 'partnerCode', 'cmdCode']:
        number_of_params[param] = len(params[param].split(','))

    longest_param = max(number_of_params, key=number_of_params.get)
    params2 = params.copy()
    print('params[longest_param]: ', params[longest_param])
    print(f"params[longest_param].split(','): {params[longest_param].split(',')}")
    print(f"len(params[longest_param].split(',')): {len(params[longest_param].split(','))}")
    print(f"len(params[longest_param].split(','))/2: {len(params[longest_param].split(','))/2}")
    params[longest_param] = ','.join(params[longest_param].split(',')[:int(len(params[longest_param].split(','))/2)])
    params2[longest_param] = ','.join(params2[longest_param].split(',')[int(len(params2[longest_param].split(','))/2):])
    for param in [params, params2]:
        try:
            response = requests.get(url='https://comtradeapi.un.org/data/v1/get/C/A/HS', headers=headers, params=param,
                                    timeout=200)
            try:
                small_df = pd.json_normalize(response.json()['data'])
                df = pd.concat([df, small_df])
            except NameError:
                df = pd.json_normalize(response.json()['data'])
            time.sleep(30)
        except requests.exceptions.Timeout:
            df = divide_response(headers, param)
    return df


def sort_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Sorts dataframe by reporter, partner, period, commodity code and flow code"""
    """Ask if the user wants to sort the output table and in which order. Return sorted dataframe."""
    dataframe = dataframe.sort_values(by='reporterDesc,partnerDesc,period,cmdCode,flowCode'.split(','))

    return dataframe


def clean_data_hs_sitc(df: pd.DataFrame) -> pd.DataFrame:
    """Deletes irrelevant columns from the dataframe."""
    keys_to_erase = ['typeCode', 'refYear', 'freqCode', 'refPeriodId',
                     'refMonth', 'reporterISO', 'flowCode', 'partnerISO',
                     'partner2Code', 'partner2ISO', 'partner2Desc',
                     'classificationCode', 'classificationSearchCode',
                     'isOriginalClassification', 'aggrLevel', 'isLeaf',
                     'customsCode', 'customsDesc', 'mosCode', 'motCode',
                     'motDesc', 'qtyUnitCode', 'qtyUnitAbbr', 'qty',
                     'isQtyEstimated', 'altQtyUnitCode', 'altQtyUnitAbbr',
                     'altQty', 'isAltQtyEstimated', 'netWgt',
                     'isNetWgtEstimated', 'grossWgt', 'isGrossWgtEstimated',
                     'legacyEstimationFlag', 'isReported', 'isAggregate',
                     'reporterCode', 'partnerCode', 'cmdDesc', 'cifvalue',
                     'fobvalue']
    df = df.drop(columns=keys_to_erase)
    df.rename(columns={'period': 'Period', 'reporterDesc': 'Reporter', 'flowDesc': 'Trade flow',
                       'partnerDesc': 'Partner', 'cmdCode': 'Commodity code', 'primaryValue': 'Trade value'},
              inplace=True)
    return df


def group_by_hs_chapters(df: pd.DataFrame, output_file_name: str) -> None:
    """
    Groups the dataframe by HS chapters and saves the data in different sheets of an Excel table
    """
    cmd_groups = ['TOTAL', '01-05', '06-14', '15', '16-24', '25-27', '28-38',
                  '39-40', '41-43', '44-49', '50-63', '64-67', '68-70', '71',
                  '72-83', '84-85', '86-89', '90-92', '93', '94-96', '97']
    cmd_group_names = ['TOTAL', 'Animal&Animal Products', 'Vegetable Products',
                       'Animal&Vegetable fats&oils',
                       'Foodstuffs', 'Mineral Products',
                       'Chemicals&Allied Industries', 'Plastics&Rubbers',
                       'Hides,Skins,Leather&Furs',
                       'Wood&Wood Products', 'Textiles', 'Footwear&Headgear',
                       'Stone&Glass', 'Precious stones&metals', 'Metals',
                       'Machinery&Electrical', 'Transportation',
                       'Optics,medical,musical&watches', 'Arms',
                       'Miscellaneous manufactures', 'Works of art']
    cmd_tuples = list(zip(cmd_groups, cmd_group_names))
    for cmd_group, name in cmd_tuples:
        if cmd_group.isalpha() or len(cmd_group) == 2:
            try:
                small_df = df.loc[df['Commodity code'] == cmd_group]
                try:
                    with pd.ExcelWriter(fr'{output_file_name}.xlsx', mode='a') as writer:
                        small_df.to_excel(writer, sheet_name=name, index=False)
                except FileNotFoundError:
                    with pd.ExcelWriter(fr'{output_file_name}.xlsx', mode='w') as writer:
                        small_df.to_excel(writer, sheet_name=name, index=False)
            except KeyError:
                pass
        else:
            small_df = pd.DataFrame(columns=df.columns)
            range_boundaries = cmd_group.split('-')
            codes_range = range(int(range_boundaries[0]),
                                int(range_boundaries[1]) + 1)
            for acode in codes_range:
                if len(str(acode)) == 2:
                    add_df = df.loc[df['Commodity code'] == str(acode)]
                else:
                    add_df = df.loc[df['Commodity code'] == f'0{str(acode)}']
                small_df = pd.concat((small_df, add_df))
            try:
                with pd.ExcelWriter(fr'{output_file_name}.xlsx', mode='a') as writer:
                    small_df.to_excel(writer, sheet_name=name, index=False)
            except FileNotFoundError:
                with pd.ExcelWriter(fr'{output_file_name}.xlsx', mode='w') as writer:
                    small_df.to_excel(writer, sheet_name=name, index=False)


def save_df(df: pd.DataFrame, output_file_name: str, file_extension: str) -> None:
    if file_extension == 'xlsx':
        try:
            os.remove(fr'{output_file_name}.xlsx')
        except FileNotFoundError:
            pass
        df.to_excel(fr'{output_file_name}.xlsx', index=False)
    else:
        try:
            os.remove(fr'{output_file_name}.csv')
        except FileNotFoundError:
            pass
        df.to_csv(fr'{output_file_name}.csv', index=False)
