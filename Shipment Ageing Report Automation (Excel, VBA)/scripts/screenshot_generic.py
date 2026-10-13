"""
Generic screenshot via a throwaway copy of the workbook (more reliable
than screenshotting the live .xlsm directly in this environment).
"""
import os
import sys
import shutil
import time
import win32com.client as win32

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSM_PATH = os.path.join(HERE, "Shipment_Ageing_Report.xlsm")


def run(sheet_name, range_ref, out_png, zoom=100):
    temp_path = os.path.join(HERE, f"_temp_shot_{sheet_name.replace(' ', '')}.xlsm")
    shutil.copyfile(XLSM_PATH, temp_path)

    xl = win32.Dispatch("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    wb = None
    try:
        wb = xl.Workbooks.Open(temp_path)
        ws = wb.Worksheets(sheet_name)
        # delete any Form Control buttons anywhere in the workbook -- they
        # seem to break CopyPicture even on sheets that don't show them
        for s in wb.Worksheets:
            try:
                for b in list(s.Buttons()):
                    b.Delete()
            except Exception:
                pass
        other = wb.Worksheets(1) if wb.Worksheets(1).Name != sheet_name else wb.Worksheets(wb.Worksheets.Count)
        try:
            ws.Columns("N:O").Hidden = False
        except Exception:
            pass
        try:
            ws.UsedRange.Value = ws.UsedRange.Value  # flatten any PivotTables to static values
        except Exception as e:
            print("flatten skipped:", e)
        other.Activate()
        ws.Activate()
        xl.ActiveWindow.Zoom = zoom
        xl.CalculateFullRebuild()
        time.sleep(3)

        rng = ws.Range(range_ref)
        last_err = None
        for attempt in range(5):
            co = None
            try:
                rng.CopyPicture(Appearance=1, Format=2)
                time.sleep(1.5 + attempt)
                co = ws.ChartObjects().Add(0, 0, rng.Width, rng.Height)
                time.sleep(0.5)
                co.Chart.Paste()
                time.sleep(0.5)
                co.Chart.Export(out_png)
                co.Delete()
                print("exported", out_png)
                last_err = None
                break
            except Exception as e:
                last_err = e
                if co is not None:
                    try:
                        co.Delete()
                    except Exception:
                        pass
        if last_err is not None:
            raise last_err
    finally:
        if wb is not None:
            wb.Close(SaveChanges=False)
        xl.Quit()
        try:
            os.remove(temp_path)
        except Exception:
            pass


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 100)
