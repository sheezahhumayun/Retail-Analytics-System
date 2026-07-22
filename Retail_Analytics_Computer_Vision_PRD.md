# Product Requirements Document (PRD)

# Retail Analytics Using Computer Vision

**Document Version:** 1.0  
**Product Category:** Computer Vision Analytics Platform  
**Target Platform:** Visibility Vision  
**Target Users:** Retail stores, supermarkets, shopping outlets, convenience stores, and multi-branch retail chains  
**Development Model:** End-to-End Computer Vision Web Application  

---

## 1. Product Overview

Retail Analytics is a computer vision-based system that transforms existing CCTV camera feeds into actionable information about customer movement, store traffic, occupancy, queues, and customer behavior.

The system processes live or recorded video streams using computer vision models and presents analytics through a centralized web dashboard.

The project should be developed as a complete standalone application while following a modular architecture that allows its computer vision services to be integrated into the broader **Visibility Vision** platform later.

The initial version will focus on reliable, measurable retail analytics rather than advanced customer identification.

---

## 2. Problem Statement

Retail businesses typically have CCTV cameras installed primarily for security. These cameras continuously generate valuable visual data, but most of this data is never analyzed.

Retail managers often cannot easily answer questions such as:

- How many customers visited today?
- What are the busiest hours?
- How long do customers stay?
- Which areas receive the most traffic?
- Where do customers spend the most time?
- How long are checkout queues?
- How many people are currently inside the store?
- Which areas are underutilized?
- How does customer traffic change between days?

Traditional solutions often require additional sensors or specialized hardware.

The Retail Analytics system should extract these insights directly from existing CCTV camera feeds wherever camera placement and video quality are suitable.

---

## 3. Product Vision

Build a reusable computer vision analytics system that converts retail CCTV streams into structured events, metrics, and visual insights.

The system should provide:

**Camera Feed → Computer Vision Inference → Tracking → Analytics Events → Data Storage → Dashboard → Alerts and Reports**

The architecture must allow new computer vision analytics modules to be added without redesigning the entire platform.

---

## 4. Product Goals

The system should:

1. Detect people in retail environments.
2. Track individuals anonymously across frames.
3. Count store entries and exits.
4. Measure real-time occupancy.
5. Generate customer traffic trends.
6. Analyze customer movement within defined zones.
7. Generate heatmaps of customer activity.
8. Measure dwell time within areas of interest.
9. Detect and analyze checkout queues.
10. Provide historical analytics through a web dashboard.
11. Support recorded videos, video files, and RTSP camera streams.
12. Store structured analytics rather than unnecessary raw video.
13. Provide APIs for future integration with Visibility Vision.
14. Maintain a modular computer vision architecture.

---

## 5. Non-Goals for MVP

The first version should not focus on:

- Facial recognition
- Customer identity recognition
- Emotion recognition
- Demographic profiling
- Individual customer identification across separate visits
- Theft detection
- Employee productivity monitoring
- Product-level interaction recognition
- Fully autonomous loss prevention

These capabilities may be explored separately in future modules.

---

## 6. Target Users

### Store Manager

Needs visibility into:

- Daily visitors
- Current occupancy
- Peak hours
- Queue conditions
- High-traffic areas

### Operations Manager

Needs:

- Historical trends
- Store performance comparisons
- Customer flow analysis
- Queue analytics
- Operational bottlenecks

### Retail Analyst

Needs:

- Traffic patterns
- Zone analytics
- Dwell-time analysis
- Historical comparisons
- Exportable data

### System Administrator

Needs:

- Camera management
- Zone configuration
- User management
- Model configuration
- System health monitoring

---

## 7. Core System Modules

1. Camera Management
2. Video Processing
3. Person Detection
4. Multi-Object Tracking
5. Entry and Exit Counting
6. Occupancy Analytics
7. Zone Analytics
8. Dwell-Time Analytics
9. Heatmap Generation
10. Queue Analytics
11. Analytics Engine
12. Event Storage
13. Dashboard
14. Reporting
15. Alerting
16. System Administration

Each module should be independently maintainable.

---

## 8. Functional Requirements

### FR-01: Camera Management

The system must allow administrators to add and manage cameras.

Each camera should contain:

- Camera ID
- Camera name
- Store ID
- Location
- RTSP URL or video source
- Camera type
- Resolution
- FPS
- Status
- Assigned analytics modules

Users should be able to add, edit, delete, enable, disable, and test cameras.

Camera states:

- Online
- Offline
- Processing
- Error
- Disabled

---

## 9. Video Input Support

The system should support:

### Live Streams

- RTSP CCTV streams

### Recorded Sources

- MP4
- AVI
- MOV

### Development Sources

- Webcam
- Uploaded test videos

The video processing layer should expose a common interface so analytics modules do not depend directly on the input source.

---

## 10. Person Detection

The system must detect people within camera frames.

Recommended model families include:

- YOLO
- RT-DETR
- Other optimized object detection models

The system should return:

- Bounding box
- Confidence score
- Class
- Timestamp
- Camera ID

The detection model should be replaceable without changing downstream analytics modules.

---

## 11. Multi-Object Tracking

The system must assign temporary tracking IDs to detected individuals.

Possible tracking algorithms:

- ByteTrack
- BoT-SORT
- DeepSORT

Tracking IDs should be anonymous and temporary.

The system should handle:

- Temporary occlusion
- Track loss
- Track re-identification within the same camera
- Duplicate track reduction

---

## 12. Entry and Exit Counting

The system must support virtual counting lines.

Administrators should be able to draw a line on the camera image and configure its direction.

When a tracked person crosses the line:

- Outside → Inside = Entry
- Inside → Outside = Exit

The system should record:

- Camera ID
- Track ID
- Event type
- Timestamp

---

## 13. Occupancy Analytics

The system should calculate:

`Current Occupancy = Total Entries - Total Exits`

Dashboard metrics should include:

- Current occupancy
- Today's visitors
- Today's exits
- Peak occupancy
- Peak occupancy time

Occupancy should be available at store level and, where technically possible, zone level.

---

## 14. Zone Management

Administrators must be able to define polygon-based zones.

Example zones:

- Entrance
- Electronics
- Clothing
- Grocery
- Promotional Area
- Checkout
- Waiting Area

Each zone should contain:

- Zone ID
- Zone Name
- Camera ID
- Polygon Coordinates
- Zone Type
- Analytics Enabled

The system should detect zone entry, exit, and presence events.

---

## 15. Zone Analytics

The system should calculate:

- Zone visitors
- Current zone occupancy
- Average dwell time
- Maximum dwell time
- Minimum dwell time
- Total visits
- Traffic by hour

---

## 16. Dwell-Time Analytics

The system should measure how long tracked individuals remain within configured zones.

The system should calculate:

- Individual anonymous dwell events
- Average dwell time
- Median dwell time
- Maximum dwell time
- Dwell-time distribution

Configurable thresholds should allow dwell-time alerts or events.

---

## 17. Heatmap Generation

The system should generate visual heatmaps using:

- Person center points
- Foot-position coordinates where appropriate
- Tracking trajectories

Users should be able to select:

- Camera
- Date
- Time range

Heatmaps should identify:

- High-traffic areas
- Low-traffic areas
- Movement concentration
- Customer congregation points

The system should support heatmap overlays on a reference camera frame.

---

## 18. Customer Flow Analysis

The system should analyze movement between configured zones and generate transition statistics.

Example:

`Entrance → Promotions → Electronics → Checkout → Exit`

This should allow retailers to understand common customer movement paths.

---

## 19. Queue Analytics

A configurable queue zone should be defined for checkout or service areas.

The system should calculate:

- Current queue length
- Average queue length
- Maximum queue length
- Estimated waiting time
- Queue duration

Configurable alerts should support queue length and duration thresholds.

---

## 20. Dashboard Requirements

### KPI Cards

- Visitors Today
- Current Occupancy
- Peak Occupancy
- Average Dwell Time
- Current Queue Length
- Active Cameras

### Charts

- Visitors by Hour
- Entries vs Exits
- Occupancy Trend
- Zone Traffic
- Average Dwell Time
- Queue Length Trend

### Visual Analytics

- Store Heatmap
- Zone Performance
- Customer Flow

---

## 21. Live Analytics View

Users should be able to view processed camera streams with optional overlays for:

- Person bounding boxes
- Tracking IDs
- Zones
- Counting lines
- Current counts

Overlays should be configurable.

---

## 22. Historical Analytics

Users should be able to analyze data by:

- Hour
- Day
- Week
- Month
- Custom period

Comparisons should include:

- Today vs Yesterday
- This Week vs Last Week
- This Month vs Last Month

---

## 23. Reports

Reports should include:

- Visitor traffic
- Peak hours
- Occupancy
- Zone performance
- Dwell time
- Queue performance

Reports should support:

- On-screen viewing
- CSV export
- PDF export

Future versions may support scheduled email reports.

---

## 24. Alert Management

The system should support rule-based alerts for:

- High occupancy
- Long queues
- Camera offline conditions
- High dwell time

Alerts should include:

- Alert type
- Camera
- Zone
- Timestamp
- Severity
- Status

---

## 25. User Interface Structure

Recommended navigation:

- Overview
- Live Cameras
- Analytics
  - Traffic
  - Occupancy
  - Zones
  - Dwell Time
  - Heatmaps
  - Customer Flow
  - Queues
- Reports
- Alerts
- Configuration
  - Stores
  - Cameras
  - Zones
  - Counting Lines
- Settings

---

## 26. Multi-Store Architecture

The architecture should support:

`Organization → Store → Camera → Analytics Configuration`

Users should be able to filter analytics by:

- Organization
- Store
- Camera
- Zone

---

## 27. Analytics Event Architecture

Computer vision services should generate standardized events.

Recommended event types:

- PERSON_DETECTED
- ENTRY
- EXIT
- ZONE_ENTER
- ZONE_EXIT
- DWELL_THRESHOLD
- QUEUE_THRESHOLD
- CAMERA_OFFLINE

The event-driven architecture should allow future modules to consume analytics independently.

---

## 28. High-Level Technical Architecture

```text
CCTV / RTSP / Video
        │
        ▼
Video Ingestion Service
        │
        ▼
Frame Processing
        │
        ▼
Person Detection
        │
        ▼
Multi-Object Tracking
        │
        ├───────────────┐
        ▼               ▼
Zone Engine       Counting Engine
        │               │
        └───────┬───────┘
                ▼
         Analytics Engine
                │
                ▼
          Event Service
                │
                ▼
             Database
                │
                ▼
             REST API
                │
                ▼
          Web Dashboard
```

---

## 29. Recommended Technology Stack

### Computer Vision

- Python
- OpenCV
- PyTorch
- Ultralytics YOLO or equivalent detector
- ByteTrack or BoT-SORT

### Backend

- FastAPI
- Python

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

### Database

- PostgreSQL
- Supabase optional

### Deployment

- Docker Compose for development
- Docker and NVIDIA Container Toolkit for GPU production deployment

---

## 30. Service Architecture

The application should separate:

- Frontend
- Backend API
- Inference Engine
- Analytics Engine
- Database

Recommended repository structure:

```text
retail-analytics/
├── frontend/
├── backend/
├── inference/
├── analytics/
├── database/
├── docker/
├── tests/
├── sample-data/
└── docs/
```

---

## 31. Database Entities

At minimum:

- Organizations
- Stores
- Users
- Cameras
- Zones
- CountingLines
- Tracks
- Events
- VisitorMetrics
- OccupancyMetrics
- ZoneMetrics
- DwellEvents
- QueueMetrics
- Alerts

Raw frame-level detections should not necessarily be stored permanently. Aggregated metrics should be generated for efficient dashboard queries.

---

## 32. API Requirements

Example endpoints:

```text
GET /api/stores
POST /api/stores
GET /api/cameras
POST /api/cameras
GET /api/cameras/{id}/status
GET /api/analytics/traffic
GET /api/analytics/occupancy
GET /api/analytics/zones
GET /api/analytics/dwell
GET /api/analytics/heatmap
GET /api/analytics/queues
GET /api/events
GET /api/alerts
```

The backend should provide documented APIs using OpenAPI/Swagger.

---

## 33. Performance Requirements

### Detection Accuracy

Target person detection precision: **≥ 90%** on representative test footage.

### Counting Accuracy

Target entry/exit counting accuracy: **≥ 90%** under suitable camera placement.

### Processing

Target: **10–15 FPS per stream** for analytics workloads.

Frame skipping should be configurable.

---

## 34. Camera Placement Assumptions

### Entry Counting

Camera should clearly observe the complete entrance.

### Heatmaps

Elevated or top-down camera placement is preferred.

### Queue Detection

Checkout and waiting areas should be clearly visible.

### Zone Analytics

The complete target zone should be visible where possible.

The project documentation must explicitly describe camera placement limitations.

---

## 35. Privacy Requirements

The system should be designed around anonymous behavioral analytics.

Default principles:

- No facial recognition
- No biometric identification
- No permanent customer identity
- Temporary tracking IDs
- Configurable video retention
- Store analytics events rather than unnecessary video

---

## 36. MVP Scope

The minimum working product must include:

1. Video upload processing
2. RTSP stream support
3. Person detection
4. Multi-object tracking
5. Entry/exit counting
6. Occupancy calculation
7. Zone configuration
8. Zone analytics
9. Dwell-time calculation
10. Heatmap generation
11. Basic queue counting
12. Analytics database
13. REST API
14. Web dashboard
15. Docker deployment

---

## 37. Phase 2 Features

- Customer flow analytics
- Advanced queue analytics
- Multi-camera analytics
- Store comparison
- AI Analytics Assistant

Example natural-language questions:

- What was our busiest period yesterday?
- Which zone had the highest dwell time this week?
- When do checkout queues usually become longest?

---

## 38. Future Computer Vision Modules

The platform architecture should allow:

- Shelf Availability Detection
- Product Interaction Analytics
- Shopping Cart Detection
- Staff vs Customer Classification
- Checkout Activity Detection
- Restricted Area Detection
- Fall Detection
- Safety Monitoring
- Suspicious Behavior Detection

These modules are outside the MVP.

---

## 39. Development Milestones

### Milestone 1: Core CV Pipeline

- Video ingestion
- Person detection
- Tracking
- Annotated video output

### Milestone 2: Analytics Engine

- Entry/exit counting
- Occupancy
- Zone detection
- Dwell time

### Milestone 3: Advanced Analytics

- Heatmaps
- Queue analytics
- Historical aggregation

### Milestone 4: Backend Platform

- Database
- REST APIs
- Camera configuration
- Analytics endpoints

### Milestone 5: Web Application

- Dashboard
- Camera management
- Analytics pages
- Configuration tools

### Milestone 6: Integration and Deployment

- Docker deployment
- RTSP testing
- Performance testing
- Documentation
- Demo video

---

## 40. Testing Requirements

The team must create a labeled test dataset containing representative retail scenarios.

Testing should measure:

### Detection

- Precision
- Recall

### Tracking

- ID switches
- Track fragmentation

### Counting

- Ground truth count
- Predicted count
- Absolute error
- Counting accuracy

### Queue Analytics

- Actual queue length
- Predicted queue length
- Mean absolute error

Tests should cover:

- Low traffic
- High traffic
- Occlusion
- Different lighting
- Different camera angles
- Groups entering together

---

## 41. Required Deliverables

- Source Code
- Frontend Application
- Backend API
- Computer Vision Inference Service
- Analytics Engine
- Database Schema
- Docker Configuration
- Sample Dataset
- Test Videos
- Model Evaluation Report
- API Documentation
- Technical Documentation
- Deployment Guide
- User Guide
- Demo Video

---

## 42. Acceptance Criteria

The project will be considered complete when:

- A user can add a video or camera stream.
- People are detected and tracked.
- Entry and exit events are generated.
- Occupancy is calculated.
- Zones can be configured.
- Zone visits and dwell time are measured.
- Heatmaps are generated from tracking data.
- Queue size can be estimated.
- Analytics are stored in a database.
- Historical metrics are accessible through APIs.
- The dashboard displays real analytics.
- The complete application runs through Docker.
- The system can process representative CCTV footage reliably.
- The repository contains complete setup and technical documentation.

---

## 43. Final Demonstration Scenario

The final demonstration should:

1. Connect or upload a retail camera feed.
2. Configure an entrance counting line.
3. Configure at least three zones.
4. Start video analytics.
5. Detect and track customers.
6. Count entries and exits.
7. Display current occupancy.
8. Calculate zone visits.
9. Calculate customer dwell time.
10. Generate a store heatmap.
11. Detect checkout queue size.
12. Open the dashboard.
13. Analyze historical visitor trends.
14. Export an analytics report.

The final demonstration should prove that the project is a complete end-to-end retail analytics product, not simply a computer vision model demo.

---

## 44. Strategic Integration with Visibility Vision

The Retail Analytics project should be treated as a reusable vertical application built on top of the Visibility Vision computer vision platform.

### Reusable Platform Components

- Camera Manager
- Stream Processor
- Inference Engine
- Tracking Engine
- Zone Engine
- Event Engine
- Analytics Engine
- Alert Engine
- Dashboard Components

### Retail-Specific Components

- Footfall Analytics
- Customer Flow
- Retail Zones
- Dwell Analytics
- Retail Heatmaps
- Queue Analytics

This separation will allow future projects such as Traffic Analytics, Warehouse Analytics, Workplace Safety, and Manufacturing Vision to reuse the same underlying computer vision infrastructure instead of being developed as completely separate applications.
