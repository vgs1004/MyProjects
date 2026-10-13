import os
import win32com.client as win32

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE_PATH = os.path.join(HERE, "Shipment_Ageing_Report.xlsm")

xl = win32.Dispatch("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False
wb = None
try:
    wb = xl.Workbooks.Open(FIXTURE_PATH)
    xl.CalculateFullRebuild()
    ws = wb.Worksheets("Dashboard")
    print("Charts on Dashboard:", [co.Chart.ChartTitle.Text for co in ws.ChartObjects()])
    print()
    print("KPI B5 (Exception Lines):", ws.Range("B5").Value)
    print("KPI E5 (% Late):", ws.Range("E5").Value)
    print("KPI H5 (Avg Delay):", ws.Range("H5").Value)
    print("KPI K5 (Share 3+ Late):", ws.Range("K5").Value)
    print("KPI N5 (Top Region):", ws.Range("N5").Value)
    print()
    print("Top cities table:")
    print(ws.Range("B33:C43").Value)
finally:
    if wb is not None:
        wb.Close(SaveChanges=False)
    xl.Quit()
