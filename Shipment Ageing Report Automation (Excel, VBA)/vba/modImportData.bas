Attribute VB_Name = "modImportData"
Option Explicit

' Shared by every module: reads a single value off the Settings sheet.
Public Function GetSetting(cellAddress As String) As Variant
    GetSetting = ThisWorkbook.Sheets("Settings").Range(cellAddress).Value
End Function

' Imports the DataCo export, keeping only the 16 columns the report needs,
' and writes them to RawData in a fixed column order every other module
' relies on. Pass csvPath to skip the file picker (used for unattended runs).
Public Sub ImportData(Optional ByVal csvPath As String = "")
    Dim wsRaw As Worksheet
    Dim tempWb As Workbook
    Dim fPath As Variant
    Dim fieldInfoArr() As Variant
    Dim i As Long

    Set wsRaw = ThisWorkbook.Sheets("RawData")

    If csvPath = "" Then
        fPath = Application.GetOpenFilename("CSV Files (*.csv),*.csv", , "Select the DataCo shipment export")
        If fPath = False Then
            MsgBox "No file selected. Import canceled.", vbExclamation
            Exit Sub
        End If
        csvPath = CStr(fPath)
    End If

    Application.ScreenUpdating = False
    Application.DisplayAlerts = False

    ' FieldInfo covers all 53 source columns. Format codes: 1=General,
    ' 2=Text, 4=MDY date, 9=Skip. Everything defaults to Skip; only the
    ' 16 columns the report uses get a real type. IMPORTANT: a skipped
    ' column still occupies its ORIGINAL column letter in the output --
    ' it is left blank, not removed/compacted. So the output sheet is
    ' still 53 columns wide; the source column numbers below are also
    ' exactly where that data lands.
    ReDim fieldInfoArr(1 To 53)
    For i = 1 To 53
        fieldInfoArr(i) = Array(i, 9)
    Next i
    fieldInfoArr(2) = Array(2, 1)    ' Days for shipping (real)
    fieldInfoArr(3) = Array(3, 1)    ' Days for shipment (scheduled)
    fieldInfoArr(6) = Array(6, 2)    ' Delivery Status
    fieldInfoArr(7) = Array(7, 1)    ' Late_delivery_risk
    fieldInfoArr(9) = Array(9, 2)    ' Category Name
    fieldInfoArr(25) = Array(25, 2)  ' Market
    fieldInfoArr(26) = Array(26, 2)  ' Order City
    fieldInfoArr(27) = Array(27, 2)  ' Order Country
    fieldInfoArr(29) = Array(29, 4)  ' order date (DateOrders)
    fieldInfoArr(30) = Array(30, 1)  ' Order Id
    fieldInfoArr(34) = Array(34, 1)  ' Order Item Id
    fieldInfoArr(38) = Array(38, 1)  ' Sales
    fieldInfoArr(41) = Array(41, 2)  ' Order Region
    fieldInfoArr(43) = Array(43, 2)  ' Order Status
    fieldInfoArr(52) = Array(52, 4)  ' shipping date (DateOrders)
    fieldInfoArr(53) = Array(53, 2)  ' Shipping Mode

    Workbooks.OpenText Filename:=csvPath, Origin:=1252, StartRow:=1, _
        DataType:=xlDelimited, TextQualifier:=xlTextQualifierDoubleQuote, _
        ConsecutiveDelimiter:=False, Tab:=False, Semicolon:=False, Comma:=True, _
        Space:=False, Other:=False, FieldInfo:=fieldInfoArr, TrailingMinusNumbers:=True

    Set tempWb = ActiveWorkbook

    ' Clipboard Copy/PasteSpecial is unreliable under invisible/headless
    ' automation (no active window), so transfer via a Value array instead.
    Dim tempData As Variant
    tempData = tempWb.Sheets(1).UsedRange.Value
    tempWb.Close SaveChanges:=False

    RebuildRawData wsRaw, tempData

    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
End Sub

' Maps the 53-column-wide import (data only at the original source column
' numbers; everything else blank) directly into the fixed 16-column
' RawData layout every other module expects. Keep this mapping in sync
' with the fieldInfoArr indices above if the source columns ever change.
Private Sub RebuildRawData(ws As Worksheet, tempData As Variant)
    Dim lastRow As Long, i As Long
    Dim dst() As Variant
    Dim headers As Variant

    If UBound(tempData, 1) < 1 Then Exit Sub
    ' row 1 of tempData is the source header row -- skip it
    lastRow = UBound(tempData, 1) - 1
    If lastRow < 1 Then Exit Sub

    headers = Array("Order Id", "Order Item Id", "Order Date", "Shipping Date", _
                     "Days Real", "Days Scheduled", "Delivery Status", "Late Delivery Risk", _
                     "Order Status", "Shipping Mode", "Market", "Order Region", _
                     "Order Country", "Order City", "Category Name", "Sales")

    ReDim dst(1 To lastRow, 1 To 16)
    For i = 1 To lastRow
        dst(i, 1) = tempData(i + 1, 30)   ' Order Id
        dst(i, 2) = tempData(i + 1, 34)   ' Order Item Id
        dst(i, 3) = tempData(i + 1, 29)   ' Order Date
        dst(i, 4) = tempData(i + 1, 52)   ' Shipping Date
        dst(i, 5) = tempData(i + 1, 2)    ' Days Real
        dst(i, 6) = tempData(i + 1, 3)    ' Days Scheduled
        dst(i, 7) = tempData(i + 1, 6)    ' Delivery Status
        dst(i, 8) = tempData(i + 1, 7)    ' Late Delivery Risk
        dst(i, 9) = tempData(i + 1, 43)   ' Order Status
        dst(i, 10) = tempData(i + 1, 53)  ' Shipping Mode
        dst(i, 11) = tempData(i + 1, 25)  ' Market
        dst(i, 12) = tempData(i + 1, 41)  ' Order Region
        dst(i, 13) = tempData(i + 1, 27)  ' Order Country
        dst(i, 14) = tempData(i + 1, 26)  ' Order City
        dst(i, 15) = tempData(i + 1, 9)   ' Category Name
        dst(i, 16) = tempData(i + 1, 38)  ' Sales
    Next i

    ws.Cells.Clear
    ws.Range("A1").Resize(1, 16).Value = headers
    ws.Range("A2").Resize(lastRow, 16).Value = dst
    ws.Range("A1:P1").Font.Bold = True
    ws.Range("C2:D" & (lastRow + 1)).NumberFormat = "yyyy-mm-dd hh:mm"
    ws.Columns("A:P").AutoFit
End Sub
