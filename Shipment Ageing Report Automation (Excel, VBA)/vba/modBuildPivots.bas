Attribute VB_Name = "modBuildPivots"
Option Explicit

' Rebuilds the two PivotTables (Region x Ageing Bucket, Market x Shipping
' Mode) and the top-10-cities table from the Exceptions sheet. Safe to
' call on every run: existing pivots (by name) are cleared first so
' re-running never collides with yesterday's tables.
Public Sub BuildPivots()
    Dim wsExc As Worksheet, wsPiv As Worksheet
    Dim lastRow As Long
    Dim srcRange As String
    Dim pc As PivotCache
    Dim pt1 As PivotTable, pt2 As PivotTable
    Dim pivotStep As String

    On Error GoTo PivotErrHandler
    pivotStep = "setup"

    Set wsExc = ThisWorkbook.Sheets("Exceptions")
    Set wsPiv = ThisWorkbook.Sheets("Pivots")

    On Error Resume Next
    wsPiv.PivotTables("PT_RegionBucket").TableRange2.Clear
    wsPiv.PivotTables("PT_MarketShipMode").TableRange2.Clear
    On Error GoTo PivotErrHandler

    wsPiv.Cells.Clear
    wsPiv.Range("B2").Value = "Region x Ageing Bucket"
    wsPiv.Range("J2").Value = "Market x Shipping Mode"
    wsPiv.Range("B22").Value = "Top 10 Cities by Late Lines"
    wsPiv.Range("B2").Font.Bold = True: wsPiv.Range("B2").Font.Size = 12
    wsPiv.Range("J2").Font.Bold = True: wsPiv.Range("J2").Font.Size = 12
    wsPiv.Range("B22").Font.Bold = True: wsPiv.Range("B22").Font.Size = 12

    lastRow = wsExc.Cells(wsExc.Rows.Count, 1).End(xlUp).Row
    If lastRow < 2 Then Exit Sub

    srcRange = "Exceptions!$A$1:$R$" & lastRow

    ' Pivot 1: Region x Ageing Bucket
    pivotStep = "pt1"
    Set pc = ThisWorkbook.PivotCaches.Create(SourceType:=xlDatabase, SourceData:=srcRange)
    Set pt1 = pc.CreatePivotTable(TableDestination:=wsPiv.Range("B4"), TableName:="PT_RegionBucket")
    pt1.PivotFields("Order Region").Orientation = xlRowField
    pt1.PivotFields("Ageing Bucket").Orientation = xlColumnField
    With pt1.PivotFields("Order Id")
        .Orientation = xlDataField
        .Function = xlCount
        .Caption = "Count of Lines"
    End With

    ' Pivot 2: Market x Shipping Mode
    pivotStep = "pt2"
    Set pc = ThisWorkbook.PivotCaches.Create(SourceType:=xlDatabase, SourceData:=srcRange)
    Set pt2 = pc.CreatePivotTable(TableDestination:=wsPiv.Range("J4"), TableName:="PT_MarketShipMode")
    pt2.PivotFields("Market").Orientation = xlRowField
    pt2.PivotFields("Shipping Mode").Orientation = xlColumnField
    With pt2.PivotFields("Order Id")
        .Orientation = xlDataField
        .Function = xlCount
        .Caption = "Count of Lines"
    End With

    ' "Pivot" 3: top 10 cities by late lines (Ageing Bucket <> On schedule).
    ' Computed directly via a Dictionary tally rather than a true
    ' PivotTable -- AutoShow (the API for a ranked top-N pivot) turned out
    ' to be unreliable here, and this is simpler and faster anyway.
    pivotStep = "top cities"
    BuildTopCitiesTable wsExc, wsPiv, lastRow

    wsPiv.Columns("A:Z").AutoFit
    Exit Sub

PivotErrHandler:
    Err.Raise Err.Number, "modBuildPivots.BuildPivots [" & pivotStep & "]", Err.Description
End Sub

Private Sub BuildTopCitiesTable(wsExc As Worksheet, wsPiv As Worksheet, lastRow As Long)
    Dim data As Variant
    Dim dict As Object
    Dim i As Long, n As Long
    Dim city As String, bucket As String
    Dim keys() As Variant, counts() As Long
    Dim tmp As Variant, tmpL As Long

    Set dict = CreateObject("Scripting.Dictionary")
    data = wsExc.Range("A2:R" & lastRow).Value

    For i = 1 To UBound(data, 1)
        bucket = CStr(data(i, 18))
        If bucket <> "On schedule" Then
            city = CStr(data(i, 14))
            If dict.Exists(city) Then
                dict(city) = dict(city) + 1
            Else
                dict.Add city, 1
            End If
        End If
    Next i

    n = dict.Count
    If n = 0 Then Exit Sub

    keys = dict.Keys
    ReDim counts(0 To n - 1)
    For i = 0 To n - 1
        counts(i) = dict(keys(i))
    Next i

    ' selection sort descending by count -- n is at most a few hundred
    ' cities, so this is fast enough without needing a fancier algorithm
    Dim j As Long, maxIdx As Long
    For i = 0 To n - 2
        maxIdx = i
        For j = i + 1 To n - 1
            If counts(j) > counts(maxIdx) Then maxIdx = j
        Next j
        If maxIdx <> i Then
            tmpL = counts(i): counts(i) = counts(maxIdx): counts(maxIdx) = tmpL
            tmp = keys(i): keys(i) = keys(maxIdx): keys(maxIdx) = tmp
        End If
    Next i

    wsPiv.Range("B23").Value = "City"
    wsPiv.Range("C23").Value = "Count of Late Lines"
    wsPiv.Range("B23:C23").Font.Bold = True

    Dim topN As Long
    topN = Application.Min(10, n)
    For i = 0 To topN - 1
        wsPiv.Cells(24 + i, 2).Value = keys(i)
        wsPiv.Cells(24 + i, 3).Value = counts(i)
    Next i
End Sub
