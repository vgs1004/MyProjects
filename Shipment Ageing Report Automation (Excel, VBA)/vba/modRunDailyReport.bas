Attribute VB_Name = "modRunDailyReport"
Option Explicit

' Master macro: Import (first run only, or after Re-import) -> Clean and
' Filter -> Pivots -> Summary -> Export dated report -> Draft Emails
' (only if Settings!B16 = "Yes") -> Run Log entry.
'
' Pass csvPath to skip the file picker (used for unattended/automated
' runs); the Control-sheet button calls this with no argument, so a live
' user gets the normal file picker the first time RawData is empty.
' Pass silent:=True to suppress the final MsgBox -- required for any
' automated/unattended call (a MsgBox is a real modal dialog even when
' Excel.Visible = False, and will hang an automated run forever).
Public Sub RunDailyReport(Optional ByVal csvPath As String = "", Optional ByVal silent As Boolean = False)
    Dim startTime As Double
    Dim rowsIn As Long, rowsOut As Long, draftCount As Long
    Dim reportPath As String
    Dim wsControl As Worksheet, wsLog As Worksheet, wsRaw As Worksheet
    Dim nextLogRow As Long
    Dim origCalc As XlCalculation
    Dim origScreen As Boolean
    Dim draftsOnRun As String
    Dim currentStep As String

    On Error GoTo ErrHandler
    currentStep = "setup"

    Set wsControl = ThisWorkbook.Sheets("Control")
    Set wsLog = ThisWorkbook.Sheets("Run Log")
    Set wsRaw = ThisWorkbook.Sheets("RawData")

    startTime = Timer
    origScreen = Application.ScreenUpdating
    origCalc = Application.Calculation
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    Application.EnableEvents = False

    wsControl.Range("B5").Value = "Running..."
    wsControl.Range("B5").Font.Color = RGB(140, 106, 34)
    wsControl.Range("B5").Font.Bold = True

    ' 1. Import -- only if RawData is empty, so the daily run does not
    ' need to re-pick the 95 MB CSV every single time. Use the
    ' "Re-import CSV" button to force a fresh import from a new export.
    currentStep = "ImportData"
    If wsRaw.Cells(2, 1).Value = "" Then
        ImportData csvPath
    End If
    rowsIn = wsRaw.Cells(wsRaw.Rows.Count, 1).End(xlUp).Row - 1

    ' 2. Clean + filter
    currentStep = "CleanAndFilter"
    rowsOut = CleanAndFilter()

    Application.Calculation = xlCalculationAutomatic
    Application.Calculate

    ' 3. Pivots
    currentStep = "BuildPivots"
    BuildPivots

    ' 4. Summary
    currentStep = "BuildSummary"
    BuildSummary

    ' 5. Export dated report
    currentStep = "ExportReport"
    reportPath = ExportReport()

    ' 6. Draft emails -- gated by Settings!B16, so re-running the report
    ' while testing does not pop open 23 Outlook windows every time.
    currentStep = "DraftEmails"
    draftCount = 0
    draftsOnRun = UCase(Trim(CStr(GetSetting("B16"))))
    If draftsOnRun = "YES" Then
        draftCount = DraftEmails()
    End If
    currentStep = "RunLog"

    ' Run Log entry
    nextLogRow = wsLog.Cells(wsLog.Rows.Count, 1).End(xlUp).Row + 1
    If nextLogRow < 2 Then nextLogRow = 2
    wsLog.Cells(nextLogRow, 1).Value = Now
    wsLog.Cells(nextLogRow, 2).Value = CDate(GetSetting("B3"))
    wsLog.Cells(nextLogRow, 3).Value = rowsIn
    wsLog.Cells(nextLogRow, 4).Value = rowsOut
    wsLog.Cells(nextLogRow, 5).Value = Round(Timer - startTime, 1)
    wsLog.Cells(nextLogRow, 6).Value = draftCount

    ' Control sheet status
    wsControl.Range("B2").Value = Now
    wsControl.Range("B3").Value = rowsOut
    wsControl.Range("B4").Value = Round(Timer - startTime, 1) & " sec"
    wsControl.Range("B5").Value = "Done"
    wsControl.Range("B5").Font.Color = RGB(75, 97, 66)

    Application.ScreenUpdating = origScreen
    Application.Calculation = origCalc
    Application.EnableEvents = True

    If Not silent Then
        MsgBox "Run complete." & vbCrLf & _
               "Rows in: " & rowsIn & vbCrLf & _
               "Exception lines: " & rowsOut & vbCrLf & _
               "Runtime: " & Round(Timer - startTime, 1) & " sec" & vbCrLf & _
               "Email drafts created: " & draftCount & " (Settings!B16 = " & draftsOnRun & ")" & vbCrLf & vbCrLf & _
               "Report saved to:" & vbCrLf & reportPath, vbInformation, "Run Daily Report"
    End If

    Exit Sub

ErrHandler:
    Application.ScreenUpdating = origScreen
    Application.Calculation = origCalc
    Application.EnableEvents = True
    wsControl.Range("B5").Value = "ERROR"
    wsControl.Range("B5").Font.Color = RGB(140, 75, 58)
    wsControl.Range("B6").Value = "[" & currentStep & "] " & Err.Source & ": " & Err.Description
    If Not silent Then
        MsgBox "Run Daily Report failed:" & vbCrLf & Err.Description, vbCritical, "Error"
    End If
End Sub

' Secondary button: forces a fresh CSV import regardless of whether
' RawData already has data (use this when a new day's export arrives).
Public Sub ReimportCsv()
    ImportData
    MsgBox "Re-import complete. Click Run Daily Report to process it.", vbInformation
End Sub

' Secondary button: drafts emails on demand, independent of the
' Settings!B16 toggle and without re-running the whole pipeline.
Public Sub RunDraftEmailsOnly()
    Dim n As Long
    n = DraftEmails()
    MsgBox n & " email draft(s) created in Outlook (not sent).", vbInformation
End Sub
