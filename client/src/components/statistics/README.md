# Statistics Feature

## Overview
The Statistics page provides comprehensive analytics and insights about the audio transcription database. It visualizes key metrics to help track progress, understand data distribution, and monitor contributor activities.

## Features

### 1. Summary Cards
- **Total Videos**: Number of YouTube videos processed
- **Total Audio Clips**: Number of audio clips generated
- **Total Duration**: Cumulative duration of all audio clips (in hours)
- **Transcribed Duration**: Duration of transcribed content with transcription count

### 2. Category Duration Chart
- Visual representation of audio duration by category/domain
- Shows clip count and video count per category
- Horizontal bar charts for easy comparison
- Categories sorted by total duration (descending)

### 3. Transcription Status
- Overview of transcribed vs non-transcribed audio clips
- Visual progress bar showing transcription completion rate
- Detailed statistics for both transcribed and non-transcribed content
- Duration metrics for each category

### 4. Daily Transcription Graph
- Timeline view of transcription activity
- Shows daily transcription counts over configurable time periods (7-365 days)
- Interactive tooltips with detailed information
- Color-coded bars (weekends in purple, weekdays in blue)
- Statistics summary (total, average per day, total hours)

### 5. Admin Contribution Chart
- Breakdown of contributions by admin users
- Non-admin contributions grouped together
- Shows transcription count, duration, and percentage for each contributor
- Visual progress bars for easy comparison
- Avatar icons for visual identification

## API Endpoints

### Get All Statistics
```
GET /api/v1/statistics?days=30
```
Returns all statistics data including summary, categories, transcription status, daily trends, and admin contributions.

**Query Parameters:**
- `days` (optional): Number of days for daily statistics (default: 30, min: 1, max: 365)

### Get Summary Only
```
GET /api/v1/statistics/summary
```
Returns only the summary statistics (videos, clips, durations).

### Get Category Durations
```
GET /api/v1/statistics/categories
```
Returns duration statistics grouped by category.

### Get Transcription Status
```
GET /api/v1/statistics/transcription-status
```
Returns transcribed vs non-transcribed statistics.

### Get Daily Transcriptions
```
GET /api/v1/statistics/daily?days=30
```
Returns daily transcription trends.

### Get Admin Contributions
```
GET /api/v1/statistics/admin-contributions
```
Returns contribution statistics by admin.

## Database Queries

All duration calculations use the `padded_duration` field from the `Audio` table, NOT the original video duration. This ensures accurate representation of the actual audio clip data.

### Key Query Logic:
- **Category Durations**: Joins `YouTube_Video` and `Audio` tables, groups by domain
- **Transcription Status**: Checks for existence of records in `Transcriptions` table
- **Daily Trends**: Groups transcriptions by creation date (cast to date)
- **Admin Contributions**: Groups by admin field, with non-admin users aggregated

## UI Components

### File Structure
```
client/src/
├── components/
│   └── statistics/
│       ├── SummaryCards.tsx
│       ├── CategoryDurationChart.tsx
│       ├── TranscriptionStatusChart.tsx
│       ├── DailyTranscriptionGraph.tsx
│       ├── AdminContributionChart.tsx
│       └── index.ts
├── pages/
│   └── StatisticsPage.tsx
├── lib/
│   └── statisticsApi.ts
└── components/
    └── Navigation.tsx
```

## Usage

### Accessing the Statistics Page
1. Click the "Statistics" button in the navigation bar
2. The page will load automatically, fetching data from the backend
3. Use the time period selector to adjust the daily transcription graph range
4. Click "Refresh" to reload the data

### Navigation
- Home button returns to the audio processing interface
- Statistics button opens the analytics dashboard

## Design Principles

1. **Clean & Modular**: Each visualization is a separate, reusable component
2. **Material-UI**: Consistent design using MUI components
3. **Responsive**: Adapts to different screen sizes
4. **Interactive**: Hover effects and tooltips for detailed information
5. **Performance**: Efficient queries and minimal re-renders

## Future Enhancements

Potential additions:
- Export statistics to PDF/CSV
- More granular filtering (by date range, category, admin)
- Real-time updates using WebSockets
- Comparison views (month-over-month, year-over-year)
- Language-specific statistics (if applicable)
- Audio quality metrics
- Speaker demographics
