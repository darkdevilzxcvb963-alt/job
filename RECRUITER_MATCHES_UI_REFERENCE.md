# 🎨 Recruiter Matches UI - Visual Reference

## Component Structure

```
┌─────────────────────────────────────────────────────────────┐
│  MATCHES PAGE                                               │
│  "Match Results"                                            │
│  "Find top candidate matches for your jobs"                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────── MATCH CONTROLS ──────┐                           │
│  │                             │                           │
│  │  [📄 CANDIDATE] [💼 JOB]   │  (Tab selector)          │
│  │                             │                           │
│  │  [Select Your Job dropdown] │  (For recruiters)        │
│  │                             │                           │
│  └────────────────────────────┘                           │
│                                                             │
│  ┌────── JOB INFO PANEL ──────────────────────┐          │
│  │  Senior Full Stack Developer               │          │
│  │  Tech Innovations Inc.                     │          │
│  │  📍 San Francisco, CA   💼 Full-time      │          │
│  └────────────────────────────────────────────┘          │
│                                                             │
│  2 Matching Candidates Found                              │
│                                                             │
│  ┌─────────────────────────────────────────┐             │
│  │  ┌───┐  Alice Johnson                   │ [88%] ✓    │
│  │  │ A │  jobseeker@example.com           │ ■■■■■■░   │
│  │  └───┘                                  │ (GREEN)    │
│  └─────────────────────────────────────────┘             │
│  │ EXPANDED:                                             │
│  │  🎯 Semantic Match: 92% ████████████░░ ✓            │
│  │  🔧 Skills Match: 88% ███████████░░░ ✓              │
│  │  📚 Experience Level: 85% ██████████░░░ ✓            │
│  │                                                      │
│  │  💡 Why This Match?                                 │
│  │  "Strong match! Alice has extensive full stack      │
│  │   experience with Python, JavaScript, React,        │
│  │   and FastAPI..."                                   │
│  │                                                      │
│  │  [📧 Contact] [👁️ View Resume] [⭐ Save]           │
│  └─────────────────────────────────────────┘             │
│                                                             │
│  ┌─────────────────────────────────────────┐             │
│  │  ┌───┐  Bob Martinez                    │ [82%] ◄   │
│  │  │ B │  bob.engineer@example.com        │ ■■■■■░░   │
│  │  └───┘                                  │ (AMBER)    │
│  └─────────────────────────────────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Color-Coded Score System

### Match Score Display

```
┌─ EXCELLENT MATCH (80-100%) ──────────┐
│  ████████████████░░░░                │
│  Color: #10b981 (Green)              │
│  [Score Circle] 88%                  │
│  ✓ "Strong match!"                   │
└──────────────────────────────────────┘

┌─ GOOD MATCH (60-79%) ─────────────────┐
│  ████████████░░░░░░░░░░              │
│  Color: #f59e0b (Amber)              │
│  [Score Circle] 72%                  │
│  ~ "Decent match"                    │
└───────────────────────────────────────┘

┌─ FAIR MATCH (0-59%) ──────────────────┐
│  ████████░░░░░░░░░░░░░░░░░░░         │
│  Color: #ef4444 (Red)                │
│  [Score Circle] 45%                  │
│  ✗ "Potential fit"                   │
└──────────────────────────────────────┘
```

## Card States

### Collapsed Card
```
┌─────────────────────────────────────────┐
│ ┌─────┐ Alice Johnson      [88%] ✓     │
│ │  A  │ jobseeker@example.com           │
│ └─────┘ █████████████░░░░░░░ (GREEN)   │
│                           [Click to expand] │
└─────────────────────────────────────────┘
```

### Expanded Card
```
┌─────────────────────────────────────────┐
│ ┌─────┐ Alice Johnson      [88%] ✓     │
│ │  A  │ jobseeker@example.com           │
│ └─────┘ ─────────────────────────────   │
│                                         │
│ ┌───────────────────────────────────┐  │
│ │ SCORE BREAKDOWN                   │  │
│ │                                   │  │
│ │ 🎯 Semantic Match: 92%           │  │
│ │    ████████████░░░░ [92%]        │  │
│ │    "Resume content matches job"  │  │
│ │                                   │  │
│ │ 🔧 Skills Match: 88%             │  │
│ │    ███████████░░░░░░ [88%]       │  │
│ │    "Required skills overlap"     │  │
│ │                                   │  │
│ │ 📚 Experience Level: 85%         │  │
│ │    ██████████░░░░░░░ [85%]       │  │
│ │    "Experience matches job"      │  │
│ └───────────────────────────────────┘  │
│                                         │
│ ┌───────────────────────────────────┐  │
│ │ 💡 Why This Match?                │  │
│ │ Strong match! Alice has extensive │  │
│ │ full stack experience with Python,│  │
│ │ JavaScript, React, and FastAPI.   │  │
│ │ Her experience level and skills   │  │
│ │ closely match the position.       │  │
│ └───────────────────────────────────┘  │
│                                         │
│ [📧 Contact] [👁️ View] [⭐ Save]     │
└─────────────────────────────────────────┘
```

## Job Dropdown States

### Closed
```
┌────────────────────────────────┐
│ Select Your Job ▼              │
└────────────────────────────────┘
```

### Open
```
┌────────────────────────────────┐
│ Select Your Job ▼              │
├────────────────────────────────┤
│ ○ Senior Full Stack Developer  │
│ ○ Backend Engineer             │
│ ○ Frontend Developer           │
└────────────────────────────────┘
```

### Selected
```
┌────────────────────────────────┐
│ ✓ Senior Full Stack Developer ▼│
└────────────────────────────────┘
```

## Screen Layout - Desktop

```
WIDTH: 1400px

┌──────────────────────────────────────────────────┐
│                                                  │
│  HEADER                                          │
│  Match Results                                   │
│  Find top candidate matches for your jobs       │
│                                                  │
├──────────────────────────────────────────────────┤
│                                                  │
│  [📄 CANDIDATE] [💼 JOB] ← Tab Selector        │
│                                                  │
│  Label: Select Your Job                         │
│  ┌────────────────────────────────┐            │
│  │ Senior Full Stack Developer ▼  │            │
│  └────────────────────────────────┘            │
│                                                  │
├──────────────────────────────────────────────────┤
│                                                  │
│  Job Info Panel (if job selected):              │
│  • Senior Full Stack Developer                  │
│  • Tech Innovations Inc.                        │
│  • 📍 San Francisco, CA  💰 $140K-$200K       │
│                                                  │
├──────────────────────────────────────────────────┤
│                                                  │
│  2 Matching Candidates Found                    │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ [Avatar] Name         [Score] [88%] ✓    │  │
│  │          email@example.com                 │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ [Avatar] Name         [Score] [82%] ~    │  │
│  │          email@example.com                 │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Screen Layout - Mobile

```
WIDTH: 375px

┌─────────────────────┐
│ Match Results       │
│ Find top candidate  │
│ matches...          │
├─────────────────────┤
│ [📄] [💼]          │
├─────────────────────┤
│ Select Job ▼        │
├─────────────────────┤
│ 2 Candidates Found  │
├─────────────────────┤
│ ┌─────────────────┐ │
│ │ [A] Alice   88% │ │
│ │     alice@...   │ │
│ │ [Expand] ▼      │ │
│ └─────────────────┘ │
├─────────────────────┤
│ ┌─────────────────┐ │
│ │ [B] Bob     82% │ │
│ │     bob@...     │ │
│ │ [Expand] ▼      │ │
│ └─────────────────┘ │
└─────────────────────┘
```

## Interaction Flow

### User Journey Map

```
START
  ↓
┌─────────────────────────────┐
│  Login as Recruiter         │ ← recruiter@example.com
│                             │   Recruiter@1234
└─────────────────────────────┘
  ↓
┌─────────────────────────────┐
│  Redirected to /jobs        │
│  See "Matches" tab/link     │
└─────────────────────────────┘
  ↓
┌─────────────────────────────┐
│  Click Matches              │
│  Load Matches page          │
│  "Job Matches" selected     │
└─────────────────────────────┘
  ↓
┌─────────────────────────────┐
│  See job dropdown           │
│  Shows recruiter's jobs:    │
│  • Senior Full Stack Dev    │
│  • Backend Engineer         │
│  • Frontend Developer       │
└─────────────────────────────┘
  ↓
┌─────────────────────────────┐
│  Select job from dropdown   │
│  "Senior Full Stack Dev"    │
└─────────────────────────────┘
  ↓
┌─────────────────────────────┐
│  See Job Info Panel         │
│  • Title                    │
│  • Company                  │
│  • Location                 │
│  • Type                     │
└─────────────────────────────┘
  ↓
┌─────────────────────────────┐
│  See Match Results          │
│  "2 Candidates Found"       │
│  • Alice: 88% (Green)       │
│  • Bob: 82% (Amber)         │
└─────────────────────────────┘
  ↓
┌─────────────────────────────┐
│  Click Alice's card         │
│  → Card expands             │
└─────────────────────────────┘
  ↓
┌─────────────────────────────┐
│  See Detailed Scores        │
│  • Semantic: 92%            │
│  • Skills: 88%              │
│  • Experience: 85%          │
│  • Explanation text         │
└─────────────────────────────┘
  ↓
┌─────────────────────────────┐
│  Click Action Buttons       │
│  • Contact Candidate        │
│  • View Resume              │
│  • Save for Later           │
└─────────────────────────────┘
  ↓
END (Future: Email sent / Modal opened / Saved)
```

## Color Palette

```
Primary Colors:
  Gradient Purple: #667eea → #764ba2
  
Semantic Colors:
  Success Green:  #10b981 (80%+)
  Warning Amber:  #f59e0b (60-80%)
  Danger Red:     #ef4444 (<60%)
  
Neutral Colors:
  Text Dark:      #2c3e50
  Text Medium:    #6c757d
  Background:     #f5f7fa
  Border:         #e9ecef
  White:          #ffffff
  
Button Colors:
  Contact:        Gradient #667eea → #764ba2
  View Resume:    Gradient #f093fb → #f5576c
  Save:           Border #ffc107, bg white
```

## Typography

```
Headings:
  H1: 2.5rem, 700 weight
  H2: 1.75rem, 600 weight
  H3: 1.25rem, 600 weight
  H4: 1rem, 600 weight

Body:
  Regular: 1rem, 400 weight
  Labels: 0.95rem, 500 weight
  Small: 0.85rem, 400 weight
  Captions: 0.9rem, 400 italic

Font Stack: System fonts (default browser)
```

## Spacing System

```
Padding:
  Containers: 2rem (32px)
  Cards: 1.5rem (24px) header, 2rem (32px) content
  Small items: 0.75rem (12px)

Margins:
  Bottom spacing: 1.5rem (24px)
  Gap between items: 1rem (16px)
  Top spacing: 2rem (32px)

Border Radius:
  Large: 16px (containers, cards)
  Medium: 12px (inputs)
  Small: 8px (buttons)
```

## Animations

```
Transitions:
  All: 0.3s ease
  Width: 0.3s ease
  

Keyframes:
  slideDown: 0.3s ease
    From: opacity 0, translateY -10px
    To: opacity 1, translateY 0
    
  spin: 1s linear infinite
    Rotation 0° → 360°

Hover Effects:
  Cards: translateY(-4px)
  Buttons: translateY(-2px)
```

## Responsive Breakpoints

```
Desktop:  1400px max-width
Tablet:   1024px breakpoint
Mobile:   768px breakpoint

Adjustments:
  Large: Side-by-side layouts
  Medium: Single column, adjusted sizing
  Small: Full-width, stacked layout
```

---

This visual reference helps understand the complete UI/UX of the recruiter matches feature!
