"""
Exports a PNG screenshot of a worksheet range via COM automation (no
screenshot API in Excel; this copies the range as a picture into a temp
chart and exports the chart image).
"""
import sys
import time
import win32com.client as win32


def export_range_png(xlsx_path, sheet_name, range_ref, out_png, zoom=100):
    xl = win32.Dispatch("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    wb = None
    try:
        wb = xl.Workbooks.Open(xlsx_path)
        xl.CalculateFullRebuild()
        ws = wb.Worksheets(sheet_name)
        other = wb.Worksheets(1) if wb.Worksheets(1).Name != sheet_name else wb.Worksheets(wb.Worksheets.Count)
        other.Activate()
        ws.Activate()
        xl.ActiveWindow.Zoom = zoom
        time.sleep(5)  # let conditional formatting / redraw settle before the first capture
        rng = ws.Range(range_ref)
        last_err = None
        for attempt in range(4):
            co = None
            try:
                rng.CopyPicture(Appearance=1, Format=2)  # xlScreen=1, xlBitmap=2
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
            try:
                wb.Close(SaveChanges=False)
            except Exception:
                pass
        xl.Quit()


if __name__ == "__main__":
    export_range_png(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
                      zoom=int(sys.argv[5]) if len(sys.argv) > 5 else 100)
