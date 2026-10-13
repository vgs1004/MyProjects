"""
Takes Shipment_Ageing_Report_base.xlsx, converts it to a macro-enabled
.xlsm, imports the 7 VBA modules from vba/*.bas, adds the 3 Control-sheet
buttons, then does one unattended end-to-end test run (passing the CSV
path directly, so no file-picker dialog blocks the automated run) and
saves.

Requires: Excel > File > Options > Trust Center > Trust Center Settings
> Macro Settings > "Trust access to the VBA project object model".
"""
import os
import sys
import time

import win32com.client as win32

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_XLSX = os.path.join(HERE, "Shipment_Ageing_Report_base.xlsx")
XLSM_PATH = os.path.join(HERE, "Shipment_Ageing_Report.xlsm")
VBA_DIR = os.path.join(HERE, "vba")
CSV_PATH = os.path.join(HERE, "Data", "DataCoSupplyChainDataset.csv")

MODULES = [
    "modImportData.bas", "modCleanAndFilter.bas", "modBuildDashboard.bas",
    "modExportReport.bas", "modDraftEmails.bas", "modRunDailyReport.bas",
]

xl = win32.Dispatch("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False
xl.AutomationSecurity = 1  # msoAutomationSecurityLow -- allow macros in this automated session

wb = None
success = False
try:
    wb = xl.Workbooks.Open(BASE_XLSX)

    # --- check VBOM trust before doing anything destructive ---
    try:
        _ = wb.VBProject.Name
    except Exception as e:
        print("VBOM access blocked:", e)
        print("Enable: Excel > File > Options > Trust Center > Trust Center Settings")
        print("> Macro Settings > 'Trust access to the VBA project object model', then rerun.")
        wb.Close(SaveChanges=False)
        xl.Quit()
        sys.exit(1)

    # Save as macro-enabled workbook first (52 = xlOpenXMLWorkbookMacroEnabled)
    wb.SaveAs(XLSM_PATH, FileFormat=52)

    # --- import the 7 modules ---
    vbp = wb.VBProject
    # remove any modules from a previous run of this script, so re-running
    # doesn't throw "name already exists"
    for comp in list(vbp.VBComponents):
        if comp.Name.startswith("mod"):
            vbp.VBComponents.Remove(comp)
    for fname in MODULES:
        path = os.path.join(VBA_DIR, fname)
        vbp.VBComponents.Import(path)
        print("imported", fname)

    wb.Save()

    # --- add the 3 Control-sheet buttons ---
    ws_control = wb.Worksheets("Control")
    for btn in ws_control.Buttons():
        btn.Delete()

    left0 = ws_control.Range("D6").Left
    top0 = ws_control.Range("D6").Top

    def add_button(top_offset, caption, macro):
        b = ws_control.Buttons().Add(left0, top0 + top_offset, 200, 32)
        b.OnAction = macro
        b.Characters.Text = caption
        return b

    add_button(0, "Run Daily Report", "RunDailyReport")
    add_button(44, "Re-import CSV (new export)", "ReimportCsv")
    add_button(88, "Draft Emails Only", "RunDraftEmailsOnly")

    wb.Save()
    print("Buttons added. Running an unattended end-to-end test (Settings!B16=No, so no Outlook drafts)...")

    # --- unattended end-to-end test run ---
    t0 = time.time()
    xl.Run("modRunDailyReport.RunDailyReport", CSV_PATH, True)  # silent=True: no blocking MsgBox
    print(f"Test run finished in {time.time() - t0:.1f}s (wall clock, includes the 95MB CSV import)")

    # Dashboard should be what the user sees first on open, not Control
    wb.Worksheets("Dashboard").Activate()

    wb.Save()
    success = True
    print("Done. Saved", XLSM_PATH)
finally:
    if wb is not None:
        try:
            wb.Close(SaveChanges=success)
        except Exception:
            pass
    xl.Quit()
