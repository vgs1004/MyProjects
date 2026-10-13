Attribute VB_Name = "modBuildDashboard"
Option Explicit

' Builds the Dashboard sheet's charts and the Top Region KPI value, all
' computed from one array read of the Exceptions sheet (same array-based
' approach as CleanAndFilter -- no PivotTables, no cell-by-cell loops).
' Chart source data lives in columns T onward, off to the side of the
' visible dashboard area the charts float over.
Public Sub BuildDashboard()
    Dim wsExc As Worksheet, wsDash As Worksheet
    Dim lastRow As Long
    Dim data As Variant
    Dim buildStep As String

    On Error GoTo DashErrHandler
    buildStep = "setup"

    Set wsExc = ThisWorkbook.Sheets("Exceptions")
    Set wsDash = ThisWorkbook.Sheets("Dashboard")

    ' clear everything except the KPI card block (rows 1-8) and any old
    ' chart objects, so re-running never duplicates charts
    Dim co As ChartObject
    For Each co In wsDash.ChartObjects
        co.Delete
    Next co
    wsDash.Rows("10:200").Clear
    wsDash.Range("T1:AZ60").Clear

    lastRow = wsExc.Cells(wsExc.Rows.Count, 1).End(xlUp).Row
    If lastRow < 2 Then Exit Sub
    data = wsExc.Range("A2:R" & lastRow).Value

    buildStep = "aggregate"
    Dim bucketKeys() As String, bucketCounts() As Long
    Dim regionKeys() As Variant, regionCounts() As Long
    Dim marketKeys() As Variant, marketCounts() As Long
    Dim weekLabels() As String, weekCounts() As Long
    Dim topRegion As String

    Aggregate data, bucketKeys, bucketCounts, regionKeys, regionCounts, _
               marketKeys, marketCounts, weekLabels, weekCounts, topRegion

    wsDash.Range("N5").Value = topRegion

    buildStep = "write chart source tables"
    WriteSourceTableStr wsDash, "T4", "Bucket", "Count", bucketKeys, bucketCounts
    Dim topRegionKeys() As Variant, topRegionCounts() As Long
    TopN regionKeys, regionCounts, 10, topRegionKeys, topRegionCounts
    WriteSourceTable wsDash, "W4", "Region", "Count", topRegionKeys, topRegionCounts
    WriteSourceTable wsDash, "Z4", "Market", "Count", marketKeys, marketCounts
    WriteSourceTableStr wsDash, "AC4", "Week", "Count", weekLabels, weekCounts

    buildStep = "charts"
    Dim gridTop As Double, gridLeft As Double
    Dim chartW As Double, chartH As Double, gapX As Double, gapY As Double
    gridTop = wsDash.Range("B10").Top
    gridLeft = wsDash.Range("B10").Left
    chartW = 330: chartH = 220: gapX = 20: gapY = 20

    BuildDonut wsDash, gridLeft, gridTop, chartW, chartH, _
        "T4", "T5:T" & (4 + UBound(bucketKeys) + 1), "U5:U" & (4 + UBound(bucketKeys) + 1), _
        "Exceptions by Ageing Bucket"

    BuildBar wsDash, gridLeft + chartW + gapX, gridTop, chartW, chartH, True, _
        "W4", "W5:W" & (4 + UBound(topRegionKeys) + 1), "X5:X" & (4 + UBound(topRegionKeys) + 1), _
        "Top Regions by Exception Count", RGB(67, 97, 238)

    BuildBar wsDash, gridLeft, gridTop + chartH + gapY, chartW, chartH, False, _
        "Z4", "Z5:Z" & (4 + UBound(marketKeys) + 1), "AA5:AA" & (4 + UBound(marketKeys) + 1), _
        "Exceptions by Market", RGB(114, 9, 183)

    BuildLine wsDash, gridLeft + chartW + gapX, gridTop + chartH + gapY, chartW, chartH, _
        "AC4", "AC5:AC" & (4 + UBound(weekLabels) + 1), "AD5:AD" & (4 + UBound(weekLabels) + 1), _
        "Exceptions by Week (lookback window)", RGB(247, 37, 133)

    buildStep = "top cities table"
    BuildTopCitiesTable data, wsDash

    Exit Sub

DashErrHandler:
    Err.Raise Err.Number, "modBuildDashboard.BuildDashboard [" & buildStep & "]", Err.Description
End Sub

' ---------- aggregation ----------

Private Sub Aggregate(data As Variant, _
        ByRef bucketKeys() As String, ByRef bucketCounts() As Long, _
        ByRef regionKeys() As Variant, ByRef regionCounts() As Long, _
        ByRef marketKeys() As Variant, ByRef marketCounts() As Long, _
        ByRef weekLabels() As String, ByRef weekCounts() As Long, _
        ByRef topRegion As String)

    Dim bucketOrder As Variant
    bucketOrder = Array("On schedule", "1 day late", "2 days late", "3+ days late")
    ReDim bucketCounts(0 To 3)
    ReDim bucketKeys(0 To 3)
    Dim k As Long
    For k = 0 To 3
        bucketKeys(k) = bucketOrder(k)
    Next k

    Dim regionDict As Object, marketDict As Object
    Set regionDict = CreateObject("Scripting.Dictionary")
    Set marketDict = CreateObject("Scripting.Dictionary")

    Dim reportDate As Date, windowStart As Date
    reportDate = CDate(GetSetting("B3"))
    windowStart = reportDate - CLng(GetSetting("B4"))
    Dim nWeeks As Long
    nWeeks = 5
    ReDim weekCounts(0 To nWeeks - 1)
    ReDim weekLabels(0 To nWeeks - 1)
    Dim wLbl As Long
    For wLbl = 0 To nWeeks - 1
        weekLabels(wLbl) = "Wk " & (wLbl + 1)
    Next wLbl

    Dim i As Long, bucket As String, region As Variant, market As Variant
    Dim shipDate As Variant, wk As Long
    Dim totalSpan As Double
    totalSpan = reportDate - windowStart

    For i = 1 To UBound(data, 1)
        bucket = CStr(data(i, 18))
        For k = 0 To 3
            If bucket = bucketKeys(k) Then
                bucketCounts(k) = bucketCounts(k) + 1
                Exit For
            End If
        Next k

        region = data(i, 12)
        If regionDict.Exists(region) Then
            regionDict(region) = regionDict(region) + 1
        Else
            regionDict.Add region, 1
        End If

        market = data(i, 11)
        If marketDict.Exists(market) Then
            marketDict(market) = marketDict(market) + 1
        Else
            marketDict.Add market, 1
        End If

        shipDate = data(i, 4)
        If IsDate(shipDate) And totalSpan > 0 Then
            wk = Int((CDate(shipDate) - windowStart) / (totalSpan / nWeeks))
            If wk < 0 Then wk = 0
            If wk > nWeeks - 1 Then wk = nWeeks - 1
            weekCounts(wk) = weekCounts(wk) + 1
        End If
    Next i

    regionKeys = regionDict.Keys
    Dim rc() As Long
    ReDim rc(0 To regionDict.Count - 1)
    For i = 0 To regionDict.Count - 1
        rc(i) = regionDict(regionKeys(i))
    Next i
    regionCounts = rc

    marketKeys = marketDict.Keys
    Dim mc() As Long
    ReDim mc(0 To marketDict.Count - 1)
    For i = 0 To marketDict.Count - 1
        mc(i) = marketDict(marketKeys(i))
    Next i
    marketCounts = mc

    ' top region by count
    Dim bestIdx As Long
    bestIdx = 0
    For i = 1 To UBound(regionCounts)
        If regionCounts(i) > regionCounts(bestIdx) Then bestIdx = i
    Next i
    If regionDict.Count > 0 Then
        topRegion = CStr(regionKeys(bestIdx))
    Else
        topRegion = ""
    End If
End Sub

Private Sub TopN(keys() As Variant, counts() As Long, n As Long, _
                  ByRef outKeys() As Variant, ByRef outCounts() As Long)
    Dim k() As Variant, c() As Long
    k = keys
    c = counts
    Dim i As Long, j As Long, maxIdx As Long, tmpV As Variant, tmpL As Long
    Dim total As Long
    total = UBound(c) + 1
    For i = 0 To total - 2
        maxIdx = i
        For j = i + 1 To total - 1
            If c(j) > c(maxIdx) Then maxIdx = j
        Next j
        If maxIdx <> i Then
            tmpL = c(i): c(i) = c(maxIdx): c(maxIdx) = tmpL
            tmpV = k(i): k(i) = k(maxIdx): k(maxIdx) = tmpV
        End If
    Next i

    Dim topCount As Long
    topCount = Application.Min(n, total)
    ReDim outKeys(0 To topCount - 1)
    ReDim outCounts(0 To topCount - 1)
    For i = 0 To topCount - 1
        outKeys(i) = k(i)
        outCounts(i) = c(i)
    Next i
End Sub

' ---------- writing small chart-source tables ----------

Private Sub WriteSourceTable(ws As Worksheet, startCell As String, h1 As String, h2 As String, _
                              keys() As Variant, counts() As Long)
    Dim topLeft As Range
    Set topLeft = ws.Range(startCell)
    topLeft.Value = h1
    topLeft.Offset(0, 1).Value = h2
    topLeft.Font.Bold = True
    topLeft.Offset(0, 1).Font.Bold = True
    Dim i As Long
    For i = 0 To UBound(keys)
        topLeft.Offset(i + 1, 0).Value = keys(i)
        topLeft.Offset(i + 1, 1).Value = counts(i)
    Next i
End Sub

Private Sub WriteSourceTableStr(ws As Worksheet, startCell As String, h1 As String, h2 As String, _
                                 keys() As String, counts() As Long)
    Dim topLeft As Range
    Set topLeft = ws.Range(startCell)
    topLeft.Value = h1
    topLeft.Offset(0, 1).Value = h2
    topLeft.Font.Bold = True
    topLeft.Offset(0, 1).Font.Bold = True
    Dim i As Long
    For i = 0 To UBound(keys)
        topLeft.Offset(i + 1, 0).Value = keys(i)
        topLeft.Offset(i + 1, 1).Value = counts(i)
    Next i
End Sub

' ---------- charts (plain ChartObjects, not PivotCharts -- more reliable) ----------

Private Sub StyleChart(cht As Chart, title As String)
    cht.HasTitle = True
    cht.ChartTitle.Text = title
    cht.ChartTitle.Font.Size = 11
    cht.ChartTitle.Font.Bold = True
    cht.ChartTitle.Font.Color = RGB(31, 36, 48)
    On Error Resume Next
    cht.ChartArea.Format.Line.Visible = False
    On Error GoTo 0
End Sub

Private Sub BuildDonut(ws As Worksheet, left As Double, top As Double, w As Double, h As Double, _
                        hdrCell As String, catRange As String, valRange As String, title As String)
    Dim co As ChartObject
    Set co = ws.ChartObjects.Add(left, top, w, h)
    co.Chart.SetSourceData Source:=ws.Range(valRange)
    co.Chart.SeriesCollection(1).XValues = ws.Range(catRange)
    co.Chart.ChartType = xlDoughnut
    StyleChart co.Chart, title

    Dim colors As Variant
    colors = Array(RGB(42, 157, 143), RGB(244, 162, 97), RGB(231, 111, 81), RGB(214, 40, 40))
    Dim s As Series
    Set s = co.Chart.SeriesCollection(1)
    Dim i As Long
    For i = 1 To s.Points.Count
        On Error Resume Next
        s.Points(i).Format.Fill.ForeColor.RGB = colors((i - 1) Mod 4)
        On Error GoTo 0
    Next i
End Sub

Private Sub BuildBar(ws As Worksheet, left As Double, top As Double, w As Double, h As Double, _
                      horizontal As Boolean, hdrCell As String, catRange As String, valRange As String, _
                      title As String, color As Long)
    Dim co As ChartObject
    Set co = ws.ChartObjects.Add(left, top, w, h)
    co.Chart.SetSourceData Source:=ws.Range(valRange)
    co.Chart.SeriesCollection(1).XValues = ws.Range(catRange)
    co.Chart.ChartType = IIf(horizontal, xlBarClustered, xlColumnClustered)
    co.Chart.SeriesCollection(1).Format.Fill.ForeColor.RGB = color
    co.Chart.HasLegend = False
    StyleChart co.Chart, title
End Sub

Private Sub BuildLine(ws As Worksheet, left As Double, top As Double, w As Double, h As Double, _
                       hdrCell As String, catRange As String, valRange As String, title As String, color As Long)
    Dim co As ChartObject
    Set co = ws.ChartObjects.Add(left, top, w, h)
    co.Chart.SetSourceData Source:=ws.Range(valRange)
    co.Chart.SeriesCollection(1).XValues = ws.Range(catRange)
    co.Chart.ChartType = xlLineMarkers
    co.Chart.SeriesCollection(1).Format.Line.ForeColor.RGB = color
    co.Chart.SeriesCollection(1).MarkerStyle = xlMarkerStyleCircle
    co.Chart.SeriesCollection(1).MarkerForegroundColor = color
    co.Chart.SeriesCollection(1).MarkerBackgroundColor = color
    co.Chart.HasLegend = False
    StyleChart co.Chart, title
End Sub

' ---------- top 10 cities table (clean, compact, banded) ----------

Private Sub BuildTopCitiesTable(data As Variant, ws As Worksheet)
    Dim dict As Object
    Set dict = CreateObject("Scripting.Dictionary")
    Dim i As Long, city As String, bucket As String
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
    If dict.Count = 0 Then Exit Sub

    Dim keys() As Variant, counts() As Long
    keys = dict.Keys
    ReDim counts(0 To dict.Count - 1)
    For i = 0 To dict.Count - 1
        counts(i) = dict(keys(i))
    Next i

    Dim topKeys() As Variant, topCounts() As Long
    TopN keys, counts, 10, topKeys, topCounts

    ws.Range("B32").Value = "Top 10 Cities by Late Lines"
    ws.Range("B32").Font.Bold = True
    ws.Range("B32").Font.Size = 12
    ws.Range("B33").Value = "City"
    ws.Range("C33").Value = "Late Lines"
    ws.Range("B33:C33").Font.Bold = True
    ws.Range("B33:C33").Interior.Color = RGB(31, 36, 48)
    ws.Range("B33:C33").Font.Color = RGB(255, 255, 255)

    For i = 0 To UBound(topKeys)
        ws.Cells(34 + i, 2).Value = topKeys(i)
        ws.Cells(34 + i, 3).Value = topCounts(i)
        If i Mod 2 = 1 Then
            ws.Range(ws.Cells(34 + i, 2), ws.Cells(34 + i, 3)).Interior.Color = RGB(244, 246, 250)
        End If
    Next i
    ws.Columns("B").ColumnWidth = 22
    ws.Columns("C").ColumnWidth = 14
End Sub
