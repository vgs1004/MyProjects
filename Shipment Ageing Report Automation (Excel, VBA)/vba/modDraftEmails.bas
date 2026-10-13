Attribute VB_Name = "modDraftEmails"
Option Explicit

' Creates one Outlook draft per region that has pending exception lines,
' each with a small attachment of just that region's rows. Uses .Display
' ONLY -- this never calls .Send. A person reviews and sends every draft
' by hand. Returns the number of drafts created.
Public Function DraftEmails() As Long
    Dim wsExc As Worksheet, wsSet As Worksheet
    Dim lastRow As Long, lastRegionRow As Long
    Dim i As Long, r As Long, outCount As Long
    Dim region As String, email As String, subject As String, bodyText As String
    Dim olApp As Object, olMail As Object
    Dim tempWb As Workbook, tempWs As Worksheet
    Dim headerRow As Variant
    Dim draftsMade As Long
    Dim attachPath As String
    Dim excData As Variant, regionRow() As Variant
    Dim j As Long

    Set wsExc = ThisWorkbook.Sheets("Exceptions")
    Set wsSet = ThisWorkbook.Sheets("Settings")

    lastRow = wsExc.Cells(wsExc.Rows.Count, 1).End(xlUp).Row
    If lastRow < 2 Then
        DraftEmails = 0
        Exit Function
    End If

    subject = CStr(GetSetting("B13"))
    bodyText = CStr(GetSetting("B14"))

    On Error Resume Next
    Set olApp = GetObject(, "Outlook.Application")
    If olApp Is Nothing Then Set olApp = CreateObject("Outlook.Application")
    On Error GoTo 0
    If olApp Is Nothing Then
        MsgBox "Could not start Outlook. Email drafts were not created.", vbExclamation
        DraftEmails = 0
        Exit Function
    End If

    lastRegionRow = wsSet.Cells(wsSet.Rows.Count, "A").End(xlUp).Row
    draftsMade = 0
    headerRow = wsExc.Range("A1:R1").Value
    ' read all exception rows once (array, not clipboard) -- Order Region is column L (12)
    excData = wsExc.Range("A2:R" & lastRow).Value

    Application.ScreenUpdating = False

    For r = 18 To lastRegionRow
        region = Trim(CStr(wsSet.Cells(r, "A").Value))
        email = Trim(CStr(wsSet.Cells(r, "B").Value))
        If region = "" Then GoTo NextRegion

        outCount = 0
        For i = 1 To UBound(excData, 1)
            If Trim(CStr(excData(i, 12))) = region Then outCount = outCount + 1
        Next i

        If outCount = 0 Then GoTo NextRegion

        ReDim regionRow(1 To outCount, 1 To 18)
        outCount = 0
        For i = 1 To UBound(excData, 1)
            If Trim(CStr(excData(i, 12))) = region Then
                outCount = outCount + 1
                For j = 1 To 18
                    regionRow(outCount, j) = excData(i, j)
                Next j
            End If
        Next i

        Set tempWb = Workbooks.Add(xlWBATWorksheet)
        Set tempWs = tempWb.Sheets(1)
        tempWs.Name = "Pending"
        tempWs.Range("A1").Resize(1, 18).Value = headerRow
        tempWs.Range("A2").Resize(outCount, 18).Value = regionRow
        tempWs.Columns.AutoFit
        attachPath = Environ$("TEMP") & "\Pending_" & CleanFileName(region) & ".xlsx"
        Application.DisplayAlerts = False
        tempWb.SaveAs Filename:=attachPath, FileFormat:=xlOpenXMLWorkbook
        tempWb.Close SaveChanges:=False
        Application.DisplayAlerts = True

        Set olMail = olApp.CreateItem(0) ' olMailItem
        With olMail
            .To = email
            .Subject = subject & " - " & region & " (" & outCount & " pending)"
            .Body = bodyText & vbCrLf & vbCrLf & _
                    region & ": " & outCount & " pending shipment lines attached." & vbCrLf & _
                    "Report date: " & Format(CDate(GetSetting("B3")), "yyyy-mm-dd")
            .Attachments.Add attachPath
            .Display
        End With

        draftsMade = draftsMade + 1
NextRegion:
    Next r

    Application.ScreenUpdating = True
    DraftEmails = draftsMade
End Function

Private Function CleanFileName(s As String) As String
    Dim badChars As Variant, c As Variant
    badChars = Array("\", "/", ":", "*", "?", """", "<", ">", "|", " ")
    CleanFileName = s
    For Each c In badChars
        CleanFileName = Replace(CleanFileName, c, "_")
    Next c
End Function
