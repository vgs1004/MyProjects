Attribute VB_Name = "modBuildSummary"
Option Explicit

' The KPI cards themselves are live formulas (set up once, at workbook
' build time) referencing the Exceptions sheet, so they do not need VBA
' to compute their values -- they just recalculate. BuildSummary's job is
' the conditional part: colouring the two rate-based cards by severity,
' since "42%" alone does not say whether that is good or bad.
Public Sub BuildSummary()
    Dim ws As Worksheet
    Dim pctLate As Double, share3 As Double

    Set ws = ThisWorkbook.Sheets("Summary")
    ws.Calculate

    pctLate = 0
    share3 = 0
    On Error Resume Next
    pctLate = ws.Range("B4").Value
    share3 = ws.Range("B6").Value
    On Error GoTo 0

    ColourKPI ws.Range("B4"), pctLate, 0.2, 0.5    ' % Late
    ColourKPI ws.Range("B6"), share3, 0.1, 0.25    ' Share 3+ days late
End Sub

Private Sub ColourKPI(cell As Range, val As Double, amberAt As Double, redAt As Double)
    If val >= redAt Then
        cell.Font.Color = RGB(140, 75, 58)
    ElseIf val >= amberAt Then
        cell.Font.Color = RGB(140, 106, 34)
    Else
        cell.Font.Color = RGB(75, 97, 66)
    End If
End Sub
