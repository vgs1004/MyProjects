Attribute VB_Name = "modCleanAndFilter"
Option Explicit

' Reads RawData into an array (not cell by cell -- this is what keeps a
' 180,000-row run fast), applies every rule from the Settings sheet, adds
' Delay Days and Ageing Bucket, and writes the Exceptions sheet in one
' block write. Returns the number of exception rows produced.
Public Function CleanAndFilter() As Long
    Dim wsRaw As Worksheet, wsExc As Worksheet
    Dim lastRow As Long, i As Long, outRow As Long
    Dim src As Variant, outArr() As Variant
    Dim reportDate As Date, windowStart As Date
    Dim lookbackDays As Long
    Dim excludedOrderStatus As String, excludedDeliveryStatus As String
    Dim onScheduleMax As Double, day1Max As Double, day2Max As Double
    Dim orderId As Variant, orderItemId As Variant, orderDate As Variant, shipDate As Variant
    Dim daysReal As Double, daysSched As Double
    Dim delivStatus As String, lateRisk As Variant, orderStatus As String
    Dim shipMode As String, market As String, region As String
    Dim country As String, city As String, category As String, sales As Double
    Dim delay As Double, bucket As String

    Set wsRaw = ThisWorkbook.Sheets("RawData")
    Set wsExc = ThisWorkbook.Sheets("Exceptions")

    reportDate = CDate(GetSetting("B3"))
    lookbackDays = CLng(GetSetting("B4"))
    excludedOrderStatus = "," & UCase(Replace(CStr(GetSetting("B6")), " ", "")) & ","
    excludedDeliveryStatus = "," & CStr(GetSetting("B7")) & ","
    onScheduleMax = CDbl(GetSetting("B9"))
    day1Max = CDbl(GetSetting("B10"))
    day2Max = CDbl(GetSetting("B11"))
    windowStart = reportDate - lookbackDays

    lastRow = wsRaw.Cells(wsRaw.Rows.Count, 1).End(xlUp).Row
    If lastRow < 2 Then
        CleanAndFilter = 0
        Exit Function
    End If

    src = wsRaw.Range("A2:P" & lastRow).Value
    ReDim outArr(1 To UBound(src, 1), 1 To 18)
    outRow = 0

    For i = 1 To UBound(src, 1)
        orderId = src(i, 1)
        orderItemId = src(i, 2)
        orderDate = src(i, 3)
        shipDate = src(i, 4)
        daysReal = Nz(src(i, 5))
        daysSched = Nz(src(i, 6))
        delivStatus = Trim(CStr(src(i, 7)))
        lateRisk = src(i, 8)
        orderStatus = Trim(UCase(CStr(src(i, 9))))
        shipMode = Trim(CStr(src(i, 10)))
        market = Trim(CStr(src(i, 11)))
        region = Trim(CStr(src(i, 12)))
        country = Trim(CStr(src(i, 13)))
        city = Trim(CStr(src(i, 14)))
        category = Trim(CStr(src(i, 15)))
        sales = Nz(src(i, 16))

        ' scope: shipping date inside the lookback window
        If Not IsDate(shipDate) Then GoTo ContinueLoop
        If CDate(shipDate) <= windowStart Or CDate(shipDate) > reportDate Then GoTo ContinueLoop

        ' exclude closed / not-relevant statuses (see Project Plan.md,
        ' "Filter rule fix": COMPLETE and CLOSED belong here too, or
        ' already-closed orders get wrongly flagged as pending)
        If InStr(excludedOrderStatus, "," & orderStatus & ",") > 0 Then GoTo ContinueLoop
        If InStr(excludedDeliveryStatus, "," & delivStatus & ",") > 0 Then GoTo ContinueLoop

        delay = daysReal - daysSched
        If delay <= onScheduleMax Then
            bucket = "On schedule"
        ElseIf delay <= day1Max Then
            bucket = "1 day late"
        ElseIf delay <= day2Max Then
            bucket = "2 days late"
        Else
            bucket = "3+ days late"
        End If

        outRow = outRow + 1
        outArr(outRow, 1) = orderId
        outArr(outRow, 2) = orderItemId
        outArr(outRow, 3) = orderDate
        outArr(outRow, 4) = shipDate
        outArr(outRow, 5) = daysReal
        outArr(outRow, 6) = daysSched
        outArr(outRow, 7) = delivStatus
        outArr(outRow, 8) = lateRisk
        outArr(outRow, 9) = orderStatus
        outArr(outRow, 10) = shipMode
        outArr(outRow, 11) = market
        outArr(outRow, 12) = region
        outArr(outRow, 13) = country
        outArr(outRow, 14) = city
        outArr(outRow, 15) = category
        outArr(outRow, 16) = sales
        outArr(outRow, 17) = delay
        outArr(outRow, 18) = bucket
ContinueLoop:
    Next i

    wsExc.Cells.Clear
    wsExc.Range("A1").Resize(1, 18).Value = Array("Order Id", "Order Item Id", "Order Date", _
        "Shipping Date", "Days Real", "Days Scheduled", "Delivery Status", "Late Delivery Risk", _
        "Order Status", "Shipping Mode", "Market", "Order Region", "Order Country", "Order City", _
        "Category Name", "Sales", "Delay Days", "Ageing Bucket")
    wsExc.Range("A1:R1").Font.Bold = True

    If outRow > 0 Then
        wsExc.Range("A2").Resize(outRow, 18).Value = outArr
        wsExc.Range("C2:D" & (outRow + 1)).NumberFormat = "yyyy-mm-dd hh:mm"
        ApplyAgeingFormatting wsExc, outRow
    End If

    wsExc.Columns("A:R").AutoFit
    wsExc.Range("A1").AutoFilter

    CleanAndFilter = outRow
End Function

Private Function Nz(v As Variant) As Double
    If IsNumeric(v) Then
        Nz = CDbl(v)
    Else
        Nz = 0
    End If
End Function

' RAG-style fill on the Ageing Bucket column: green / amber / orange / red.
Private Sub ApplyAgeingFormatting(ws As Worksheet, n As Long)
    Dim rng As Range
    Set rng = ws.Range("R2:R" & (n + 1))
    rng.FormatConditions.Delete

    With rng.FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="=""On schedule""")
        .Interior.Color = RGB(220, 231, 210)
        .Font.Color = RGB(75, 97, 66)
    End With
    With rng.FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="=""1 day late""")
        .Interior.Color = RGB(245, 231, 201)
        .Font.Color = RGB(140, 106, 34)
    End With
    With rng.FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="=""2 days late""")
        .Interior.Color = RGB(240, 205, 170)
        .Font.Color = RGB(153, 76, 0)
    End With
    With rng.FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="=""3+ days late""")
        .Interior.Color = RGB(240, 220, 214)
        .Font.Color = RGB(140, 75, 58)
    End With
End Sub
