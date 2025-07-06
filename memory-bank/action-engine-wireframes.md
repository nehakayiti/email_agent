# Action Engine Frontend Wireframes - Option 2 Enhanced

## Overview
This document outlines the detailed wireframe design for implementing Action Engine functionality using inline category cards with action rules. The design prioritizes intuitive user experience, contextual clarity, and delightful interactions.

## Core Design Principles

### 1. Progressive Disclosure
- Start simple, reveal complexity on demand
- Show action rules only when relevant
- Use expandable sections for detailed configuration

### 2. Visual Hierarchy
- Clear distinction between categories and their actions
- Consistent use of color coding for action types
- Prominent status indicators

### 3. Contextual Intelligence
- Show affected email counts in real-time
- Preview actions before applying
- Smart defaults based on category patterns

### 4. Delightful Interactions
- Smooth animations and transitions
- Immediate feedback for all actions
- Confirmation patterns that build trust

## Detailed Wireframe Design

### Main Categories Page Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Categories Dashboard                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ 📧 Primary                                                              │ │
│  │   12 emails • 3 unread                                                  │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ 🎯 Action Rules                                                     │ │ │
│  │  │                                                                     │ │ │
│  │  │  ┌─────────────────────────────────────────────────────────────────┐ │ │ │
│  │  │  │ 📤 Archive after 7 days                                         │ │ │ │
│  │  │  │    • 5 emails eligible for action                               │ │ │ │
│  │  │  │    • Next action: Tomorrow at 2:30 PM                           │ │ │ │
│  │  │  │                                                                  │ │ │ │
│  │  │  │  [Edit] [Preview] [Disable]                                     │ │ │ │
│  │  │  └─────────────────────────────────────────────────────────────────┘ │ │ │
│  │  │                                                                     │ │ │
│  │  │  [➕ Add Another Rule]                                              │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                         │ │
│  │  [View Emails] [Manage Rules]                                          │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ 📧 Promotions                                                           │ │
│  │   45 emails • 8 unread                                                 │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ 🎯 Action Rules                                                     │ │ │
│  │  │                                                                     │ │ │
│  │  │  ┌─────────────────────────────────────────────────────────────────┐ │ │ │
│  │  │  │ 🗑️ Trash after 3 days                                           │ │ │ │
│  │  │  │    • 12 emails eligible for action                              │ │ │ │
│  │  │  │    • Next action: Today at 4:15 PM                              │ │ │ │
│  │  │  │                                                                  │ │ │ │
│  │  │  │  [Edit] [Preview] [Disable]                                     │ │ │ │
│  │  │  └─────────────────────────────────────────────────────────────────┘ │ │ │
│  │  │                                                                     │ │ │
│  │  │  ┌─────────────────────────────────────────────────────────────────┐ │ │ │
│  │  │  │ 📤 Archive after 1 day (if not opened)                         │ │ │ │
│  │  │  │    • 8 emails eligible for action                               │ │ │ │
│  │  │  │    • Next action: In 2 hours                                    │ │ │ │
│  │  │  │                                                                  │ │ │ │
│  │  │  │  [Edit] [Preview] [Disable]                                     │ │ │ │
│  │  │  └─────────────────────────────────────────────────────────────────┘ │ │ │
│  │  │                                                                     │ │ │
│  │  │  [➕ Add Another Rule]                                              │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                         │ │
│  │  [View Emails] [Manage Rules]                                          │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ 📧 Social                                                               │ │
│  │   23 emails • 2 unread                                                 │ │
│  │                                                                         │ │
│  │  [➕ Add Action Rules] [View Emails]                                   │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Action Rule Configuration Modal

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Configure Action Rule - Promotions                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ Action Type                                                             │ │
│  │                                                                         │ │
│  │  ○ Archive  ○ Trash  ○ Mark as Read  ○ Move to Folder                  │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ 📤 Archive                                                          │ │ │
│  │  │    Move emails to archive folder                                    │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ Timing                                                                  │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ Wait for: [7] days after email is received                          │ │ │
│  │  │                                                                     │ │ │
│  │  │ ○ Apply to all emails                                               │ │ │
│  │  │ ○ Only if email is unread                                           │ │ │
│  │  │ ○ Only if email hasn't been opened                                  │ │ │
│  │  │ ○ Only if sender is not in contacts                                 │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ Preview                                                                 │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ 📧 15 emails will be affected by this rule                          │ │ │
│  │  │                                                                     │ │ │
│  │  │ • "50% off everything!" - 3 days old                               │ │ │
│  │  │ • "Limited time offer" - 5 days old                                │ │ │
│  │  │ • "Flash sale today" - 6 days old                                  │ │ │
│  │  │ • ... and 12 more                                                  │ │ │
│  │  │                                                                     │ │ │
│  │  │ Next action will be scheduled for: Tomorrow at 2:30 PM              │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ Safety Settings                                                         │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ ☑️ Show proposed actions before executing                           │ │ │
│  │  │ ☑️ Send email notification when actions are taken                   │ │ │
│  │  │ ☑️ Limit to 50 emails per day                                       │ │ │
│  │  │ ☑️ Don't act on emails from important senders                       │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [Cancel]                    [Save as Draft] [Activate Rule]               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Action Preview Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Action Preview - Promotions                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ Summary                                                                 │ │
│  │                                                                         │ │
│  │  📤 Archive after 7 days • 15 emails ready for action                  │ │
│  │                                                                         │ │
│  │  [Execute Now] [Schedule for Later] [Modify Rule]                      │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ Emails to be Archived                                                   │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ ☑️ "50% off everything!" - newsletter@store.com                     │ │ │
│  │  │    Received: 3 days ago • Unread                                    │ │ │
│  │  │                                                                     │ │ │
│  │  │  [View Email] [Exclude]                                             │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ ☑️ "Limited time offer" - deals@retailer.com                        │ │ │
│  │  │    Received: 5 days ago • Unread                                    │ │ │
│  │  │                                                                     │ │ │
│  │  │  [View Email] [Exclude]                                             │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ ☑️ "Flash sale today" - promotions@shop.com                         │ │ │
│  │  │    Received: 6 days ago • Unread                                    │ │ │
│  │  │                                                                     │ │ │
│  │  │  [View Email] [Exclude]                                             │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                         │ │
│  │  [Show More (12)]                                                       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ Bulk Actions                                                            │ │
│  │                                                                         │ │
│  │  [Select All] [Deselect All] [Exclude Selected]                        │ │
│  │                                                                         │ │
│  │  [Cancel]                    [Execute Selected (15)]                   │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Enhanced Category Card States

#### 1. No Action Rules State
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📧 Social                                                                   │
│   23 emails • 2 unread                                                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ 🎯 No action rules configured                                           │ │
│  │                                                                         │ │
│  │  [➕ Add Your First Rule]                                               │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [View Emails]                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2. Rule Disabled State
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📧 Updates                                                                  │
│   8 emails • 1 unread                                                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ 🎯 Action Rules (Disabled)                                              │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ ⏸️ Archive after 14 days                                             │ │ │
│  │  │    • Rule is currently disabled                                     │ │ │
│  │  │    • 2 emails would be affected                                     │ │ │
│  │  │                                                                     │ │ │
│  │  │  [Enable] [Edit] [Delete]                                           │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [View Emails] [Manage Rules]                                              │ │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 3. Multiple Rules State
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📧 Work                                                                     │
│   67 emails • 12 unread                                                    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ 🎯 Action Rules (2 active)                                              │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ 📤 Archive after 30 days                                             │ │ │
│  │  │    • 8 emails eligible                                               │ │ │
│  │  │    • Next: Dec 15, 2:30 PM                                          │ │ │
│  │  │                                                                     │ │ │
│  │  │  [Edit] [Preview] [Disable]                                         │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ 🗑️ Trash after 90 days                                               │ │ │
│  │  │    • 3 emails eligible                                               │ │ │
│  │  │    • Next: Jan 15, 2:30 PM                                          │ │ │
│  │  │                                                                     │ │ │
│  │  │  [Edit] [Preview] [Disable]                                         │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                         │ │
│  │  [➕ Add Another Rule]                                                  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  [View Emails] [Manage Rules]                                              │ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Interactive Elements & Micro-interactions

### 1. Hover States
- Category cards lift slightly on hover
- Action rule cards show subtle glow
- Buttons have smooth color transitions

### 2. Loading States
- Skeleton loading for email counts
- Spinner for rule processing
- Progress bars for bulk operations

### 3. Success/Error Feedback
- Toast notifications for rule changes
- Inline validation messages
- Confirmation dialogs for destructive actions

### 4. Smart Defaults
- Suggest common rule patterns based on category
- Auto-complete for sender domains
- Intelligent timing suggestions

## Responsive Design Considerations

### Mobile Layout
- Stack category cards vertically
- Collapsible action rule sections
- Touch-friendly button sizes
- Swipe gestures for quick actions

### Tablet Layout
- Two-column grid for category cards
- Side panel for rule configuration
- Optimized touch targets

### Desktop Layout
- Three-column grid for category cards
- Modal dialogs for configuration
- Keyboard shortcuts for power users

## Accessibility Features

### 1. Screen Reader Support
- Semantic HTML structure
- ARIA labels for interactive elements
- Clear focus indicators

### 2. Keyboard Navigation
- Tab order follows visual layout
- Escape key closes modals
- Enter/Space for button activation

### 3. Color & Contrast
- High contrast mode support
- Color-blind friendly palette
- Clear visual hierarchy

## Performance Optimizations

### 1. Lazy Loading
- Load email counts on demand
- Defer rule preview calculations
- Progressive image loading

### 2. Caching Strategy
- Cache category metadata
- Store user preferences locally
- Optimistic updates for better UX

### 3. Efficient Updates
- Real-time sync for email counts
- Debounced rule validation
- Batch operations for bulk actions

## Implementation Priority

### Phase 1: Core Functionality
1. Basic category cards with action rule display
2. Simple rule configuration modal
3. Basic preview functionality

### Phase 2: Enhanced UX
1. Advanced rule configuration options
2. Improved preview dashboard
3. Bulk action capabilities

### Phase 3: Polish & Optimization
1. Advanced animations and transitions
2. Performance optimizations
3. Accessibility improvements

This wireframe design creates a delightful, intuitive experience that makes email automation feel natural and trustworthy while providing users with full control and visibility into their automated actions. 