# SUMS — Frontend Design Plan
> **Stack:** Django Templates + Vanilla CSS (separate files) + Vanilla JS (separate files)  
> **Rule:** Zero inline `style=""` attributes. HTML = structure, CSS = all styling, JS = all logic.

---

## Architecture

```
Django backend (already built) exposes REST API at /api/...
Django frontend app serves HTML templates at proper URL routes
Browser loads CSS from /static/css/ and JS from /static/js/
JS fetch() calls consume the REST API using JWT tokens
```

---

## Folder Structure

```
Smart University Management System/
│
├── frontend/                    ← New Django app
│   ├── apps.py
│   ├── urls.py                  ← All page URL routes
│   └── views.py                 ← Template views (login_required guards)
│
├── templates/                   ← All HTML (at project root level)
│   ├── base.html                ← Master layout + CSS/JS includes
│   ├── partials/
│   │   ├── _sidebar.html
│   │   ├── _topbar.html
│   │   ├── _toast.html
│   │   ├── _modal.html
│   │   └── _chatbot.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── student/
│   │   ├── dashboard.html
│   │   ├── attendance.html
│   │   └── exams.html
│   ├── teacher/
│   │   ├── dashboard.html
│   │   ├── attendance.html
│   │   └── grades.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   └── departments.html
│   └── shared/
│       ├── courses.html
│       ├── notices.html
│       └── ai_tools.html
│
└── static/
    ├── css/
    │   ├── tokens.css           ← CSS custom properties (colors, spacing, fonts)
    │   ├── reset.css            ← Universal reset + base typography
    │   ├── layout.css           ← Sidebar, topbar, main content grid
    │   ├── components.css       ← Cards, buttons, badges, forms, tables, modals
    │   ├── animations.css       ← @keyframes + .anim-* utility classes
    │   ├── login.css            ← Login/Register page specific styles
    │   ├── dashboard.css        ← Hero banner + stat card color variants
    │   ├── charts.css           ← Chart.js wrapper containers
    │   ├── attendance.css       ← SVG ring + progress bar color rules
    │   └── responsive.css       ← @media breakpoints
    └── js/
        ├── api.js               ← fetch() wrapper + all endpoint methods
        ├── auth.js              ← JWT localStorage helpers
        ├── toast.js             ← toast.success/error/warning/info()
        ├── modal.js             ← modal.show() / modal.confirm() / modal.hide()
        ├── sidebar.js           ← Collapse toggle, active link
        ├── topbar.js            ← Breadcrumb, notif badge, avatar dropdown
        ├── chatbot.js           ← AI chatbot FAB + chat window
        ├── charts.js            ← makeLineChart(), makeDoughnutChart(), makeBarChart()
        ├── utils.js             ← countUp(), formatDate(), debounce(), formatGrade()
        └── pages/
            ├── login.js
            ├── student-dashboard.js
            ├── student-attendance.js
            ├── student-exams.js
            ├── teacher-dashboard.js
            ├── teacher-attendance.js
            ├── teacher-grades.js
            ├── admin-dashboard.js
            ├── admin-users.js
            ├── admin-departments.js
            ├── shared-courses.js
            ├── shared-notices.js
            └── shared-ai.js
```

---

## Design System

### Color Tokens (`tokens.css`)
```css
:root {
  /* Backgrounds */
  --bg-primary:    #0F1629;
  --bg-secondary:  #1A2540;
  --bg-tertiary:   #1E2D4A;
  --bg-glass:      rgba(255, 255, 255, 0.05);
  --bg-glass-hover:rgba(255, 255, 255, 0.08);
  --border-glass:  rgba(255, 255, 255, 0.10);
  --border-glass-bright: rgba(255, 255, 255, 0.18);

  /* Accent Colors */
  --accent-blue:    #3B82F6;
  --accent-violet:  #7C3AED;
  --accent-emerald: #10B981;
  --accent-amber:   #F59E0B;
  --accent-red:     #EF4444;
  --accent-pink:    #EC4899;

  /* Glow variants */
  --accent-blue-glow:    rgba(59, 130, 246, 0.3);
  --accent-violet-glow:  rgba(124, 58, 237, 0.3);
  --accent-emerald-glow: rgba(16, 185, 129, 0.3);
  --accent-amber-glow:   rgba(245, 158, 11, 0.3);
  --accent-red-glow:     rgba(239, 68, 68, 0.3);

  /* Gradients */
  --gradient-hero:    linear-gradient(135deg, #7C3AED 0%, #3B82F6 100%);
  --gradient-sidebar: linear-gradient(180deg, #0F1629 0%, #1A2540 100%);
  --gradient-card-blue:   linear-gradient(135deg, rgba(59,130,246,0.2), rgba(59,130,246,0.05));
  --gradient-card-violet: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(124,58,237,0.05));
  --gradient-card-emerald:linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.05));
  --gradient-card-amber:  linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.05));

  /* Text */
  --text-primary:   #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted:     #475569;

  /* Typography */
  --font-heading: 'Outfit', sans-serif;
  --font-body:    'Inter', sans-serif;

  /* Spacing */
  --s-1:4px; --s-2:8px; --s-3:12px; --s-4:16px;
  --s-5:20px; --s-6:24px; --s-8:32px; --s-10:40px;

  /* Radius */
  --r-sm:8px; --r-md:12px; --r-lg:16px; --r-xl:20px; --r-full:9999px;

  /* Glass */
  --glass-blur:      blur(20px);
  --glass-shadow:    0 8px 32px rgba(0,0,0,0.35);
  --glass-shadow-lg: 0 16px 48px rgba(0,0,0,0.45);

  /* Transitions */
  --transition-fast: 0.15s ease-out;
  --transition-base: 0.25s ease-out;

  /* Layout */
  --sidebar-width:     240px;
  --sidebar-collapsed: 64px;
  --topbar-height:     64px;
}
```

### Typography
- **Headings** → `Outfit` (600, 700, 800) — loaded via Google Fonts
- **Body/UI** → `Inter` (400, 500, 600) — loaded via Google Fonts

### Glass Card Pattern
```css
/* class="glass-card" */
background: var(--bg-glass);
border: 1px solid var(--border-glass);
border-radius: var(--r-lg);
backdrop-filter: var(--glass-blur);
box-shadow: var(--glass-shadow);
transition: transform var(--transition-fast), box-shadow var(--transition-fast);

/* class="glass-card" :hover */
transform: translateY(-3px);
box-shadow: var(--glass-shadow-lg);
```

---

## App Shell Layout

```
┌─────────────────────────────────────────────────────────┐
│  TOPBAR   [☰ | Page Title / Breadcrumb]    [🔔]  [👤]  │ h=64px sticky
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│ SIDEBAR  │         MAIN CONTENT                         │
│ w=240px  │         padding: 32px                        │
│          │                                              │
│ [icon]   │                                              │
│ [nav]    │                                              │
│ [items]  │                                              │
│          │                                              │
│ [Avatar] │                                              │
│ [Logout] │                                              │
└──────────┴──────────────────────────────────────────────┘
```

---

## Page Specs

### Login `/login/` — `templates/auth/login.html` + `static/css/login.css` + `static/js/pages/login.js`
```
LEFT PANEL (flex:1)              RIGHT PANEL (w=480px)
─────────────────────────────    ────────────────────────────────
Animated gradient background     Dark background (#0F1629)
  violet → blue → emerald        🎓 SUMS  (gradient text logo)

🎓  SUMS                         [Student] [Teacher] [Admin]  ← role pills
"Smart University..."
                                 Email: _______________
Floating particles (CSS anim)    Password: ____________
                                 [  Sign In  ] ← gradient btn
Stats: 40+ APIs | 3 AI | 5 dash
                                 ──── or ────
                                 Don't have account? Register
```

**CSS classes** (NO inline styles):
- `.login-left` — gradient bg, particle host
- `.particle` — `position:absolute`, `border-radius:50%`, `animation: particleFloat`
- `.login-right` — dark panel, centered flex
- `.role-pill` / `.role-pill.selected` — selection state via class toggle
- `.login-divider` — "or" line divider

---

### Student Dashboard `/student/dashboard/`
**API calls:** `GET /api/students/profile/`, `/api/students/cgpa/`, `/api/students/routine/`, `/api/courses/assignments/`, `/api/attendance/my-attendance/`

```
[  Hero Banner (gradient)  —  "Welcome back, John! 🎓"  —  CGPA | Attendance | Courses  ]

[ CGPA       ] [ Attendance ] [ Enrolled  ] [ Pending    ]
[ stat-card  ] [ stat-card  ] [ Courses   ] [ Assignments]
[ .violet    ] [ .emerald   ] [ .blue     ] [ .amber     ]

[ Line Chart (Chart.js)        ] [ Doughnut Chart (Chart.js)   ]
[ CGPA per semester            ] [ Grade distribution A+/A/B/F ]

[ Weekly Routine widget ]
  [ Mon ] [ Tue ] [ Wed ] [ Thu ] [ Fri ]  ← day tabs
  [Course card] [Course card] ...

[ Recent Assignments Table ]
  Course | Title | Due Date | Status (badge: submitted/pending/late)
```

---

### Student Attendance `/student/attendance/`
**API calls:** `GET /api/attendance/my-attendance/`

```
[ Summary Hero — Average % | Courses Tracked | Good Standing count ]
[ ⚠️ Warning Banner — if average < 75% ]

For each course — .glass-card row:
  [ SVG Circle Ring 80px ]   [ Course code + name        ]
  [   pct% colored text  ]   [ Status badge              ]
                             [ Present/Absent/Total count ]
                             [ Progress bar              ]

Color rules (attendance.css):
  ≥ 75%  →  --accent-emerald + emerald glow
  60–74% →  --accent-amber   + amber glow
  < 60%  →  --accent-red     + red glow
```

---

### Student Exams `/student/exams/`
**API calls:** `GET /api/exams/my-results/`

```
Results grouped by Semester → then by Exam Type (Quiz / Midterm / Final)

Each row:
  Course code | Exam type | Marks (e.g. 82/100) | [Progress bar] | Grade badge

Grade badge colours (components.css):
  A+, A   → .badge-violet
  B+, B   → .badge-blue
  C+, C   → .badge-amber
  D, F    → .badge-red
```

---

### Teacher Dashboard `/teacher/dashboard/`
**API calls:** `GET /api/teachers/profile/`, `/api/teachers/my-courses/`

```
[ Hero Banner — "Good morning, Prof. Smith!" ]
[ Courses ] [ Students ] [ Pending Gradings ] [ Notices Posted ]

[ My Courses Grid — 3 col ]
  Each card: course code/name | enrollment progress bar | [Mark Attendance] [Add Grade]

[ Quick Attendance Section ]
  Date picker + Student checklist (Present/Absent/Late toggles) + [Submit]

[ Bar Chart — score distribution for selected course ]

[ AI Tools — [Summarize Submissions] [Check Plagiarism] [At-Risk Students] ]
```

---

### Teacher Attendance `/teacher/attendance/`
**API calls:** `GET /api/courses/courses/`, `POST /api/attendance/bulk-mark/`

```
[ Course selector dropdown ]
[ Date picker input ]
[ Student List Table ]
  Student Name | ID | [ Present ] [ Absent ] [ Late ]  ← toggle buttons
[ [Submit Attendance] — gradient btn ]
[ Analytics: table sorted by attendance % ascending (at-risk first) ]
```

---

### Teacher Grades `/teacher/grades/`
**API calls:** `GET /api/courses/submissions/`, `POST /api/courses/submissions/<id>/grade/`

```
[ Course filter selector ]
[ Submissions Table ]
  Student | Assignment | Submitted | Marks | Status | [Grade] [Summarize] [Plagiarism]

[Grade] → modal: Marks input + Feedback textarea + [Save]
[Summarize] → modal: AI-generated summary text
[Plagiarism] → inline badge shows similarity %
```

---

### Admin Dashboard `/admin-panel/dashboard/`
**API calls:** `GET /api/auth/admin/users/`, `/api/auth/admin/audit-logs/`, `/api/auth/admin/login-anomalies/`

```
[ System Health Hero — Total users | Active courses | Anomalies ]
[ Users stat ] [ Courses ] [ Notices ] [ Security Alerts ]

[ User Management Table ]
  Avatar | Name | Email | Role badge | Status | [Edit] [Delete]
  Search bar + Role filter above table

[ Audit Log Viewer — scrollable ]
  Timestamp | User | Action (color dot) | Resource

[ Login Anomaly Cards ]
  Red-border glass cards — User | IP | Reason | [Mark Resolved]
```

---

### Admin Users `/admin-panel/users/`
```
[ Search input + Role filter dropdown ]
[ Users Table ]
  # | Name | Email | Role badge | Verified | Joined | [Edit] [Deactivate] [Delete]
[Edit] → modal: change role, toggle active
[Delete] → modal.confirm() → DELETE /api/auth/admin/users/<id>/
```

---

### Admin Departments `/admin-panel/departments/`
```
[ [+ Add Department] button ]
[ Departments Grid — cards per dept ]
  Dept name | Code | Head Teacher | Student count | Course count | [Edit]
[ Courses sub-table per department ]
[ [+ Add Course] → modal: code, name, credits, teacher, schedule, max_students ]
```

---

### Shared Courses `/courses/`
**API calls:** `GET /api/courses/departments/`, `/api/courses/courses/`

```
[ Filter bar — Department | Search | Semester | Year ]
[ Course Cards Grid — 3 col ]
  Course code (blue uppercase) | Course name
  👨‍🏫 Teacher name | Credits | Semester
  [████████░░] 28/40 enrolled  ← progress bar
  [Enroll]  (student) or  [Edit] [Manage]  (teacher/admin)
  Greyed [Enroll] if full or already enrolled
```

---

### Shared Notices `/notices/`
**API calls:** `GET /api/notices/`, `POST /api/notices/`

```
URGENT notices (is_urgent=True):
  Amber left-border card + 🔴 URGENT badge

Regular notices:
  Glass card — Title | Date | [Student/Teacher/All] pill | Content excerpt

Admin only: floating [+ New Notice] FAB → modal:
  Title | Content | Target Role | Department | Is Urgent checkbox
```

---

### Shared AI Tools `/ai/`
**API calls:** `GET /api/ai/weak-students/`, `/api/ai/reputation-score/`

```
[ Weak Student Prediction ]
  Table: Student | Course | Attendance% | Avg Marks | Risk badge
  🔴 High Risk  /  🟡 Medium  /  🟢 Low

[ Academic Reputation Score ]
  Per-student row + animated progress bar (0–100)
  > 80 → emerald  |  50–80 → blue  |  < 50 → amber
```

---

### AI Chatbot (Global Widget) — `_chatbot.html` + `chatbot.js`
**API:** `POST /api/ai/chatbot/`

```
Fixed bottom-right FAB (bounce animation):  🤖
Click → slide-up chat window:
  ┌─────────────────────────┐
  │ 🤖 SUMS AI     [✕]     │  ← gradient header
  ├─────────────────────────┤
  │ Bot: Hi! How can I...  │
  │              User: ...  │
  │ Bot: [spinner] thinking │
  ├─────────────────────────┤
  │ [Type question...] [➤] │
  └─────────────────────────┘
```

---

## CSS File Responsibilities

| File | What Goes In It |
|---|---|
| `tokens.css` | All `--variable` custom properties |
| `reset.css` | `*`, `body`, `a`, `button`, `input`, `img`, `ul` resets |
| `layout.css` | `#sidebar`, `.main-wrapper`, `#topbar`, `#main-content`, `.page` |
| `components.css` | `.glass-card`, `.stat-card`, `.btn`, `.badge`, `.form-control`, `.modal`, `.toast`, `.dropdown`, `.nav-item`, `.chatbot-*`, `.course-card`, `.day-tab` |
| `animations.css` | All `@keyframes`, `.anim-fadeIn`, `.anim-slideUp`, `.stagger`, `.skeleton` |
| `login.css` | `.login-left`, `.login-right`, `.particle`, `.role-pill`, `.login-divider` |
| `dashboard.css` | `.hero-banner`, `.hero-stat`, stat card color variants |
| `charts.css` | `.chart-container`, `.chart-canvas-wrapper`, `.chart-title` |
| `attendance.css` | `.attendance-ring`, SVG ring dimensions, progress color variants |
| `responsive.css` | All `@media` queries |

---

## JS File Responsibilities

| File | What It Does |
|---|---|
| `api.js` | `fetch()` wrapper with JWT, auto-refresh on 401, all endpoint methods |
| `auth.js` | `getToken()`, `getUser()`, `getRole()`, `logout()`, `isLoggedIn()` |
| `toast.js` | `toast.success/error/warning/info(title, msg)` → appends `.toast` div |
| `modal.js` | `modal.show({title,body,footer})`, `modal.confirm()`, `modal.hide()` |
| `sidebar.js` | Toggle `.collapsed` class, highlight active `.nav-item` |
| `topbar.js` | Page title update, notification badge count, avatar dropdown |
| `chatbot.js` | FAB click handler, chat message append, API call, typing indicator |
| `charts.js` | `makeLineChart(ctx, labels, data, color)`, `makeDoughnutChart()`, `makeBarChart()` |
| `utils.js` | `countUp(el, target, duration, decimals)`, `formatDate(d)`, `debounce(fn, ms)` |
| `pages/*.js` | Page-specific API calls, DOM updates, event listeners only |

---

## API Endpoints Used

| Page | Endpoint |
|---|---|
| Login | `POST /api/auth/login/` |
| Register | `POST /api/auth/register/` |
| All pages | `GET /api/auth/me/` |
| Student Dashboard | `GET /api/students/profile/`, `/api/students/cgpa/`, `/api/students/routine/` |
| Student Attendance | `GET /api/attendance/my-attendance/` |
| Student Exams | `GET /api/exams/my-results/` |
| Teacher Dashboard | `GET /api/teachers/profile/`, `/api/teachers/my-courses/` |
| Teacher Attendance | `POST /api/attendance/bulk-mark/` |
| Teacher Grades | `GET /api/courses/submissions/`, `POST /api/courses/submissions/<id>/grade/` |
| Admin Dashboard | `GET /api/auth/admin/users/`, `/api/auth/admin/audit-logs/`, `/api/auth/admin/login-anomalies/` |
| Courses | `GET /api/courses/courses/`, `POST /api/courses/enrollments/` |
| Notices | `GET /api/notices/`, `POST /api/notices/` |
| AI Tools | `GET /api/ai/weak-students/`, `/api/ai/reputation-score/` |
| Chatbot | `POST /api/ai/chatbot/` |
| AI Summary | `POST /api/ai/assignment-summary/<id>/` |
| Plagiarism | `POST /api/ai/plagiarism-check/<id>/` |

---

## Micro-Interactions & Animations

| Trigger | Animation | Duration |
|---|---|---|
| Page load | Cards stagger `.anim-slideUp` | 50ms delay per child |
| Stat numbers | `countUp()` JS counter | 1.2s |
| Chart render | Chart.js built-in draw-in | 800ms |
| Card hover | `translateY(-3px)` + shadow | 150ms ease |
| Button active | `scale(0.97)` | 100ms |
| Sidebar toggle | Width 240→64px | 250ms ease |
| Toast appear | Slide in from right | 350ms |
| Chatbot FAB | Bounce loop | 3s infinite |
| Modal open | Scale + fade in | 250ms |
| Notification bell | Shake on new notice | 600ms |

---

## Responsive Breakpoints (`responsive.css`)

| Breakpoint | Sidebar | Stat Grid | Layout |
|---|---|---|---|
| `≥ 1280px` | 240px full | 4-column | Side by side charts |
| `768–1279px` | 64px icons | 2-column | Stacked charts |
| `< 768px` | Hidden → bottom tab bar | 1-column | All stacked |

---

## Django Settings Required

```python
# config/settings.py — additions needed

INSTALLED_APPS += ['frontend']

TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']

STATICFILES_DIRS = [BASE_DIR / 'static']

LOGIN_URL = '/login/'
```

---

## Build Order

1. `frontend/` Django app + `urls.py` routes + `views.py` template views
2. `settings.py` — add static/templates dirs + `frontend` app
3. `config/urls.py` — include `frontend.urls`
4. **CSS** — `tokens.css` → `reset.css` → `layout.css` → `components.css` → `animations.css` → page CSS
5. **Core JS** — `api.js` → `auth.js` → `toast.js` → `modal.js` → `utils.js`
6. **Shell JS** — `sidebar.js` → `topbar.js` → `chatbot.js` → `charts.js`
7. **Templates** — `base.html` → partials → `auth/login.html` → all pages
8. **Page JS** — `pages/login.js` → role dashboards → remaining pages
9. **Responsive** — `responsive.css` final pass
10. **Test** — `python manage.py runserver` → open `http://127.0.0.1:8000/login/`
