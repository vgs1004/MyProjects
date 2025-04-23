# 🎮 Video Game Sales Dashboard (Power BI)

This project is a comprehensive **Video Game Sales Dashboard** created using Power BI. It provides visual insights into video game sales data, enabling users to explore trends by **genre, year, platform**, and more. The dashboard is split across **two pages: Overview** and **Detailed Analysis**.

---

## 📁 Project Structure

📦 VideoGameSalesDashboard ┣ 📊 Dashboard.pbix ┣ 📄 README.md ┗ 📈 VideoGameSalesData.xlsx


---

## 🚀 Features

### ✅ Page 1: Overview
- Logo and slicer integration for genre filtering.
- Custom hack to hide slicer scrollbar using a transparent shape overlay.
- Two charts:
  - **Sales by Genre**
  - **Sales by Region**
- Clean, minimalist layout with stylized visuals.

### ✅ Page 2: Detailed Analysis
- Duplicated layout from Overview page to maintain consistency.
- Custom height to accommodate more visuals (`1000`px).
- **Four tables** showing the top 10 games in:
  - Action
  - Adventure
  - Shooting
  - Sports genres  
- Each table styled with:
  - Light/Dark alternating row colors
  - White text
  - Rounded borders (no lines)
- **Line chart** showing yearly sales for the **top 10 platforms only**.
- **Bar charts**:
  - Best-selling games of all time
  - Best-selling games of the current decade (2010+)
- Advanced filters applied to restrict visual data scope.

---

## 🛠️ Techniques Used

- Custom scrollbar hiding using a shape overlay
- Slicer filtering
- Table formatting (style removal, row coloring)
- Top N filtering using sales as metric
- Advanced filtering on year (≥ 2010)
- Dynamic titles using text boxes
- Visual alignment, font styling, and padding adjustments

---

## 📦 Requirements

- Power BI Desktop (latest version recommended)
- `VideoGameSalesData.xlsx` as the primary data source

---

## 📊 How to Use

1. Open `Dashboard.pbix` in Power BI Desktop.
2. Ensure `VideoGameSalesData.xlsx` is available or refresh the dataset if prompted.
3. Use the slicer to filter by genre.
4. Navigate between pages (`Overview` and `Detailed Analysis`) using tabs.
5. Hover over charts/tables for tooltip insights.

---

## 📽️ Inspiration

This project is a part of a video tutorial series covering Power BI dashboard development from scratch. It demonstrates real-world practices in shaping, filtering, and designing interactive reports.

