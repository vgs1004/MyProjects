"""
Adds real Excel PivotTables, PivotCharts and slicers to the Dashboard sheet
via COM automation. Same pattern as project 02's build_dashboard.py.

Layout:
  - KPI cards: rows 4-6 (built in generate_data.py)
  - 2x2 PivotChart grid: starting ~row 10
  - Slicers (Region, RiskLevel): to the right of the chart grid
  - Supporting PivotTables: parked below, starting row 48, one per column band
"""
import sys
import win32com.client as win32

sys.path.insert(0, r"C:\Users\varsh\Projects\Portfolio\_shared")
import palette as pal

PATH = r"C:\Users\varsh\Projects\Portfolio\03-project-financial-portfolio-tracker-excel\Project_Financial_Portfolio_Tracker.xlsx"

xlDatabase = 1
xlRowField = 1
xlColumnField = 2
xlDataField = 4
xlPageField = 3
xlSum = -4157
xlAverage = -4106
xlCount = -4112
xlColumnClustered = 51
xlBarClustered = 57
xlPie = 5
xlLine = 4

xl = win32.gencache.EnsureDispatch("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False

wb = None
success = False
try:
    wb = xl.Workbooks.Open(PATH)
    xl.CalculateFullRebuild()
    ws_proj = wb.Worksheets("Projects")
    ws_res = wb.Worksheets("Resources")
    ws_ms = wb.Worksheets("MonthlySpend")
    ws_dash = wb.Worksheets("Dashboard")

    def make_table(ws, name, last_col_letter):
        last_row = ws.UsedRange.Rows.Count
        ref = f"$A$1:${last_col_letter}${last_row}"
        lo = ws.ListObjects.Add(1, ws.Range(ref), None, 1)
        lo.Name = name
        lo.TableStyle = "TableStyleMedium2"
        return lo, last_row

    lo_proj, proj_last_row = make_table(ws_proj, "ProjectsTable", "L")
    lo_res, res_last_row = make_table(ws_res, "ResourcesTable", "F")
    lo_ms, ms_last_row = make_table(ws_ms, "MonthlySpendTable", "D")

    cache_proj = wb.PivotCaches().Create(SourceType=xlDatabase, SourceData="Projects!ProjectsTable")
    cache_res = wb.PivotCaches().Create(SourceType=xlDatabase, SourceData="Resources!ResourcesTable")
    cache_ms = wb.PivotCaches().Create(SourceType=xlDatabase, SourceData="MonthlySpend!MonthlySpendTable")

    def add_value_field(pt, field_name, func, caption):
        df = pt.PivotFields(field_name)
        df.Orientation = xlDataField
        df.Function = func
        df.Caption = caption
        return df

    PIVOT_ROW = 48

    # 1. Portfolio spend vs budget by project (row=ProjectName, values=Budget & ActualSpend)
    pt1 = cache_proj.CreatePivotTable(TableDestination=ws_dash.Range(f"B{PIVOT_ROW}"), TableName="PT_SpendVsBudget")
    pt1.PivotFields("ProjectName").Orientation = xlRowField
    add_value_field(pt1, "Budget", xlSum, "Budget Amount")
    add_value_field(pt1, "ActualSpend", xlSum, "Actual Spend")

    # 2. Variance by project (row=ProjectName, value=sum Variance)
    pt2 = cache_proj.CreatePivotTable(TableDestination=ws_dash.Range(f"N{PIVOT_ROW}"), TableName="PT_VarianceByProject")
    pt2.PivotFields("ProjectName").Orientation = xlRowField
    add_value_field(pt2, "Variance", xlSum, "Variance Amount")

    # 3. Utilization by resource (row=Resource, value=avg Utilization)
    pt3 = cache_res.CreatePivotTable(TableDestination=ws_dash.Range(f"Z{PIVOT_ROW}"), TableName="PT_UtilByResource")
    pt3.PivotFields("Resource").Orientation = xlRowField
    add_value_field(pt3, "Utilization", xlAverage, "Avg Utilization")

    # 4. RAG summary count (row=ScheduleStatus, value=count of ProjectID)
    pt4 = cache_proj.CreatePivotTable(TableDestination=ws_dash.Range(f"AL{PIVOT_ROW}"), TableName="PT_RAGSummary")
    pt4.PivotFields("ScheduleStatus").Orientation = xlRowField
    add_value_field(pt4, "ProjectID", xlCount, "Project Count")

    # 5. Monthly spend trend (row=Month, value=sum ActualSpendThatMonth)
    pt5 = cache_ms.CreatePivotTable(TableDestination=ws_dash.Range(f"AX{PIVOT_ROW}"), TableName="PT_MonthlySpend")
    pt5.PivotFields("Month").Orientation = xlRowField
    add_value_field(pt5, "ActualSpendThatMonth", xlSum, "Actual Spend")

    dash_label = ws_dash.Range(f"B{PIVOT_ROW - 2}")
    dash_label.Value = "Supporting PivotTables (source data behind the charts above)"
    dash_label.Font.Italic = True
    dash_label.Font.Size = 9
    dash_label.Font.Color = pal.rgb(pal.LABEL_GRAY)

    wb.Save()

    # ---- Charts ----
    grid_top = ws_dash.Range("B10").Top
    grid_left = ws_dash.Range("B10").Left
    chart_w, chart_h = 430, 250
    gap_x, gap_y = 20, 20
    bar_extra = 90  # the horizontal bar chart (c1) needs extra width for project-name labels

    def style_chart(chart, title):
        chart.HasTitle = True
        chart.ChartTitle.Text = title
        chart.ChartTitle.Font.Color = pal.rgb(pal.INK)
        chart.ChartTitle.Font.Bold = True
        try:
            chart.ChartArea.Format.Line.Visible = False
        except Exception:
            pass

    def color_series(chart, colors):
        for i in range(1, chart.SeriesCollection().Count + 1):
            c = pal.rgb(colors[(i - 1) % len(colors)])
            s = chart.SeriesCollection(i)
            try:
                s.Format.Fill.ForeColor.RGB = c
            except Exception:
                pass
            try:
                s.Format.Line.ForeColor.RGB = c
            except Exception:
                pass

    def color_pie_points(chart, colors, n):
        s = chart.SeriesCollection(1)
        for i in range(1, n + 1):
            try:
                s.Points(i).Format.Fill.ForeColor.RGB = pal.rgb(colors[(i - 1) % len(colors)])
            except Exception:
                pass

    def add_chart(pt, left, top, width, height, chart_type, title):
        co = ws_dash.ChartObjects().Add(Left=left, Top=top, Width=width, Height=height)
        co.Chart.SetSourceData(Source=pt.TableRange2)
        co.Chart.ChartType = chart_type
        style_chart(co.Chart, title)
        return co

    c1 = add_chart(pt1, grid_left, grid_top, chart_w + bar_extra, chart_h,
                    xlBarClustered, "Spend vs Budget by Project")
    color_series(c1.Chart, [pal.FIN_TERTIARY, pal.FIN_SECONDARY])
    try:
        c1.Chart.Axes(2).TickLabels.NumberFormat = '#,##0,"K"'  # Axes(xlValue=2), regardless of orientation
    except Exception:
        pass

    c2 = add_chart(pt4, grid_left + chart_w + bar_extra + gap_x, grid_top, chart_w, chart_h,
                    xlPie, "RAG Summary: Projects by Schedule Status")
    # Pivot rows are alphabetical: Amber, Green, Red -- semantic RAG colors,
    # kept consistent with the rest of the portfolio regardless of accent set.
    color_pie_points(c2.Chart, [pal.OPEN_FONT, pal.MET_FONT, pal.BREACH_FONT], 3)

    c3 = add_chart(pt3, grid_left, grid_top + chart_h + gap_y, chart_w, chart_h,
                    xlColumnClustered, "Utilization by Resource")
    color_series(c3.Chart, [pal.FIN_PRIMARY])

    c4 = add_chart(pt5, grid_left + chart_w + bar_extra + gap_x, grid_top + chart_h + gap_y, chart_w, chart_h,
                    xlLine, "Monthly Spend Trend")
    color_series(c4.Chart, [pal.FIN_SECONDARY])
    try:
        c4.Chart.Axes(2).TickLabels.NumberFormat = '#,##0,"K"'
    except Exception:
        pass

    wb.Save()

    # ---- Slicers: Region and RiskLevel, connected across pivots where the field exists ----
    slicer_left = grid_left + 2 * chart_w + bar_extra + 2 * gap_x + 20
    slicer_top = grid_top

    sc_region = wb.SlicerCaches.Add2(pt1, "Region")
    sl1 = sc_region.Slicers.Add(SlicerDestination=ws_dash, Name="RegionSlicer", Caption="Region",
                                 Top=slicer_top, Left=slicer_left, Width=160, Height=180)
    try:
        sl1.Style = "SlicerStyleLight6"
    except Exception:
        pass
    for pt in (pt2, pt4):
        try:
            sc_region.PivotTables.AddPivotTable(pt)
        except Exception as e:
            print("region link skip:", e)

    sc_risk = wb.SlicerCaches.Add2(pt1, "RiskLevel")
    sl2 = sc_risk.Slicers.Add(SlicerDestination=ws_dash, Name="RiskSlicer", Caption="Risk Level",
                               Top=slicer_top + 190, Left=slicer_left, Width=160, Height=140)
    try:
        sl2.Style = "SlicerStyleLight6"
    except Exception:
        pass
    for pt in (pt2, pt4):
        try:
            sc_risk.PivotTables.AddPivotTable(pt)
        except Exception as e:
            print("risk link skip:", e)

    ws_dash.Activate()
    xl.ActiveWindow.View = 1
    ws_dash.Range("A1").Select()
    xl.ActiveWindow.Zoom = 85

    wb.Save()
    success = True
    print("Dashboard built.")
finally:
    if wb is not None:
        try:
            wb.Close(SaveChanges=success)  # discard partial work on failure
        except Exception:
            pass
    xl.Quit()
