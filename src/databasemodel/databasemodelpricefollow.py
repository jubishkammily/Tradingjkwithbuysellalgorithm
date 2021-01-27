import pandas as pd

class DatabaseModelPriceFollow:
    def __init__(self):
            self.status = True
            # self.list_rows = []
            self.table_csv_name = "tradefollow.csv"
            self.table_current_csv_table_name = "tradefollowcurrent.csv"
            
        

    def get_columnn_names_list(self):
        columnn_names_list = ['ShareName', 'TransactionType', 'TradePrice', 'StopLoss','Status',"TradePriceFinal"]
        return columnn_names_list
    

    def add_row_to_existing_table(self,list_row):
        print("add_row_to_existing_table",list_row)
        list_rows = []
        column_name_list = self.get_columnn_names_list()
        list_rows.append(list_row)
        print("self.list_rows",list_rows)
        df = pd.DataFrame(list_rows,columns=column_name_list)
        df.to_csv(self.table_csv_name,mode = 'a', header = False)

    
    
    def save_current_transaction(self,list_row):
        print("save_current_transaction",list_row)
        current_list_rows = []
        column_name_list = self.get_columnn_names_list()
        current_list_rows.append(list_row)
        print("current_list_rows",current_list_rows)
        df = pd.DataFrame(current_list_rows,columns=column_name_list)
        df.to_csv(self.table_current_csv_table_name,mode = 'w', header = False)

    



# test_table = DatabaseModelPriceFollow()
# list_row_test = ["SBIN","Bought4",296.2,294.9,"None"]
# test_table.add_row_to_existing_table(list_row_test)
# list_row_test = ["SBIN2","Bought5",296.2,294.9,"None"]
# test_table.add_row_to_existing_table(list_row_test)
# list_row_test = ["SBIN3","Bought3",296.2,294.9,"None"]
# test_table.add_row_to_existing_table(list_row_test)
# list_row_test = ["SBIN4","Bought4",296.2,294.9,"None"]
# test_table.add_row_to_existing_table(list_row_test)

        

  