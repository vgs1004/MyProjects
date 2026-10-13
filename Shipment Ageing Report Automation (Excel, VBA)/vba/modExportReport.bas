Attribute VB_Name = "modExportReport"
Option Explicit

' Saves a values-only copy of Exceptions and Dashboard as a dated report
' file in Reports\, so each day's report is a frozen snapshot independent
' of the live workbook. Returns the saved path.
Public Function ExportReport() As String
    Dim reportDate As Date
    Dim exportPath As String
    Dim newWb As Workbook
    Dim ws As Worksheet, newWs As Worksheet
    Dim sheetNames As Variant
    Dim i As Long

    reportDate = CDate(GetSetting("B3"))
    exportPath = ThisWorkbook.Path & "\Reports\"
    If Dir(exportPath, vbDirectory) = "" Then MkDir exportPath
    exportPath = exportPath & "Shipment_Ageing_Report_" & Format(reportDate, "yyyy-mm-dd") & ".xlsx"

    Application.ScreenUpdating = False
    Application.DisplayAlerts = False

    Set newWb = Workbooks.Add(xlWBATWorksheet)
    sheetNames = Array("Exceptions", "Dashboard")

    For i = 0 To UBound(sheetNames)
        Set ws = ThisWorkbook.Sheets(sheetNames(i))
        ws.Copy After:=newWb.Sheets(newWb.Sheets.Count)
        Set newWs = newWb.Sheets(newWb.Sheets.Count)
        ' flatten formulas and pivot table links to static values -- a
        ' direct Value self-assignment, not Copy/PasteSpecial, since
        ' clipboard operations are unreliable under headless automation
        newWs.UsedRange.Value = newWs.UsedRange.Value
    Next i

    ' remove the blank sheet Workbooks.Add created by default
    newWb.Sheets(1).Delete

    newWb.SaveAs Filename:=exportPath, FileFormat:=xlOpenXMLWorkbook
    newWb.Close SaveChanges:=False

    Application.DisplayAlerts = True
    Application.ScreenUpdating = True

    ExportReport = exportPath
End Function
